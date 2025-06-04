from __future__ import print_function, unicode_literals, division, absolute_import
import unittest
import os
import io # For Python 2/3 compatible file I/O
import six # For Python 2/3 compatibility
import json # For malformed JSON test
from smartjson.__smart_json__ import (
    SmartJson,
    SmartJsonError,
    SmartJsonSerializationError,
    SmartJsonDeserializationError,
    SmartJsonUnsupportedTypeError,
    SmartJsonCircularDependencyError,
    SmartJsonSchemaValidationError # Added
)

# --- Helper classes and Schemas for Validation Tests ---
class ValidAddress:
    def __init__(self, street, city, zip_code):
        self.street = street
        self.city = city
        self.zip_code = zip_code

VALID_ADDRESS_SCHEMA = {
    'street': {'type': six.string_types, 'required': True},
    'city': {'type': six.string_types, 'required': True},
    'zip_code': {'type': six.string_types, 'required': True}
}

class ValidItem:
    def __init__(self, item_id, price):
        self.item_id = item_id
        self.price = price

VALID_ITEM_SCHEMA = {
    'item_id': {'type': six.integer_types, 'required': True},
    'price': {'type': float, 'required': True}
}

class ValidUser:
    def __init__(self, name, age, email=None, address=None, roles=None, preferences=None, items=None):
        self.name = name
        self.age = age
        if email:
            self.email = email # Optional
        if address:
            self.address = address # Nested object
        if roles:
            self.roles = roles # List of simple types (strings)
        if preferences:
            self.preferences = preferences # Dictionary with simple values
        if items:
            self.items = items # List of objects

VALID_USER_SCHEMA = {
    'name': {'type': six.string_types, 'required': True},
    'age': {'type': six.integer_types, 'required': True},
    'email': {'type': six.string_types, 'required': False}, # Optional
    'address': { # Nested object
        'type': ValidAddress, # For serialization, specifies expected Python type
                               # For deserialization, this implies value should be a dict,
                               # and 'schema' here defines how to validate that dict.
        'required': False,
        'schema': VALID_ADDRESS_SCHEMA
    },
    'roles': { # List of simple types
        'type': list,
        'required': False,
        'item_type': six.string_types # Specifies type of items in the list
    },
    'preferences': { # Dictionary with simple value types (not explicitly validated here beyond 'dict')
        'type': dict,
        'required': False
        # Could add 'value_type': str here if we wanted to validate values of the dict itself
    },
    'items': { # List of objects
        'type': list,
        'required': False,
        'item_type': ValidItem, # For serialization, item type is ValidItem
                                # For deserialization, implies items are dicts
        'item_schema': VALID_ITEM_SCHEMA # Schema for each item in the list
    }
}


# Original Helper classes for other tests
class SimpleObject:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class CircularRefObject:
    def __init__(self, name):
        self.name = name
        self.ref = None

    def __repr__(self): # For easier debugging if a test fails unexpectedly
        return f"<CircularRefObject(name='{self.name}', id={id(self)}) ref_id={id(self.ref) if self.ref else None}>"

class ContainerObject:
    def __init__(self, name):
        self.name = name
        self.list_attr = []
        self.dict_attr = {}


class TestSmartJson(unittest.TestCase):

    def test_circular_dependency_direct(self):
        obj1 = CircularRefObject("obj1")
        obj2 = CircularRefObject("obj2")
        obj1.ref = obj2
        obj2.ref = obj1

        sj = SmartJson(obj1)
        with self.assertRaisesRegex(SmartJsonCircularDependencyError, "Circular dependency detected"):
            sj.serialize()

    def test_circular_dependency_in_list(self):
        obj1 = ContainerObject("container")
        obj_cycle = CircularRefObject("cycle_obj_in_list")
        obj_cycle.ref = obj_cycle # Self-reference

        obj1.list_attr.append(obj_cycle)

        # Add another object that references obj1 (container itself)
        obj2 = CircularRefObject("obj2_points_to_container")
        obj2.ref = obj1
        obj1.list_attr.append(obj2)


        sj_container = SmartJson(obj1)
        with self.assertRaisesRegex(SmartJsonCircularDependencyError, "Circular dependency detected"):
            sj_container.serialize()

    def test_circular_dependency_in_dict_value(self):
        obj1 = ContainerObject("container_dict_val")
        obj_cycle = CircularRefObject("cycle_obj_in_dict_val")
        obj_cycle.ref = obj_cycle

        obj1.dict_attr["cycle"] = obj_cycle

        obj2 = CircularRefObject("obj2_points_to_container_from_dict")
        obj2.ref = obj1
        obj1.dict_attr["points_up"] = obj2

        sj_container = SmartJson(obj1)
        with self.assertRaisesRegex(SmartJsonCircularDependencyError, "Circular dependency detected"):
            sj_container.serialize()

    def test_circular_dependency_in_dict_key_is_not_supported(self):
        # Note: JSON only supports string keys. SmartJson doesn't convert object keys.
        # This test is more about ensuring it doesn't break in a non-standard way.
        # The cycle would be if the object *value* associated with a key creates a cycle.
        # If an object itself was a key and could be serialized (it can't by default json),
        # that would be a different scenario. This test is similar to dict_value.
        obj1 = ContainerObject("container_dict_key_like")
        key_obj = SimpleObject("key_obj", 1) # Not actually used as object key in JSON
                                            # but its value might be an object causing cycle

        obj_cycle = CircularRefObject("cycle_obj_for_key_like")
        obj_cycle.ref = obj1 # Cycle back to container

        obj1.dict_attr[str(key_obj)] = obj_cycle

        sj_container = SmartJson(obj1)
        with self.assertRaisesRegex(SmartJsonCircularDependencyError, "Circular dependency detected"):
            sj_container.serialize()

    def test_circular_dependency_complex_nested(self):
        a = CircularRefObject("A")
        b = CircularRefObject("B")
        c = CircularRefObject("C")
        d = CircularRefObject("D")

        a.ref = b
        b.ref = [c, d] # b's ref is a list
        c.ref = a      # c refers back to a, completing the cycle
        d.ref = None

        sj = SmartJson(a)
        with self.assertRaisesRegex(SmartJsonCircularDependencyError, "Circular dependency detected"):
            sj.serialize()

    # --- Error Handling Tests ---
    def test_deserialize_file_not_found(self):
        sj = SmartJson()
        with self.assertRaisesRegex(SmartJsonDeserializationError, "JSON file not found: non_existent_file.json"):
            sj.toObjectFromFile("non_existent_file.json")

    def test_deserialize_malformed_json_string(self):
        sj = SmartJson()
        malformed_json = '{"name": "test", "value": 123,' # Missing closing brace
        # Regex to match the custom part of the message, allowing for variability in the original exception part.
        with self.assertRaisesRegex(SmartJsonDeserializationError, r"Invalid JSON format in input:.*"):
            sj.toObject(malformed_json)

    def test_deserialize_malformed_json_file(self):
        sj = SmartJson()
        malformed_json_content = '{"name": "test_file", "value": 456,'
        # Create a temporary file in the tests directory if it exists, else in current dir
        test_dir = "tests"
        if not os.path.exists(test_dir):
            # Fallback to current directory if /tests doesn't exist (e.g. running script directly)
            # This is mainly for robustness in different execution environments.
            # For proper test suite execution, 'tests' dir should exist.
            test_dir = "."

        temp_file_name = os.path.join(test_dir, "malformed_temp.json")

        try:
            with io.open(temp_file_name, "w", encoding='utf-8') as f:
                f.write(malformed_json_content)

            # Regex to match the custom part, allowing variability in the original exception part.
            # Need to escape temp_file_name if it can contain regex special characters.
            # For simplicity, assuming temp_file_name is simple.
            with self.assertRaisesRegex(SmartJsonDeserializationError, r"Invalid JSON format in file '{}':.*".format(temp_file_name)):
                sj.toObjectFromFile(temp_file_name)
        finally:
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)

    def test_unsupported_type_from_enum_conversion(self):
        # This test checks if _EnumConversion correctly raises SmartJsonUnsupportedTypeError
        # when given a non-enum type.
        try:
            # Accessing internal class for a more direct unit test
            from smartjson.__smart_json__ import SmartJson as SJ_Internal
            non_enum_obj = SimpleObject("test", 1)
            # _EnumConversion constructor expects 'visited' set
            enum_converter = SJ_Internal._EnumConversion(non_enum_obj, set())
            with self.assertRaisesRegex(SmartJsonUnsupportedTypeError, "is not a directly serializable enum"):
                enum_converter.convert()
        except ImportError:
            self.skipTest("Could not directly access _EnumConversion for isolated test.")
        except AttributeError: # If _EnumConversion is not found on SJ_Internal (e.g. name mangling)
            self.skipTest("Could not directly access _EnumConversion due to potential name mangling or structure change.")


    def test_serialization_error_from_problematic_property(self):
        # Tests if errors during attribute access (e.g., a property raising an exception)
        # are caught and wrapped in SmartJsonSerializationError by _DataTypeConversion.
        class ProblematicProperty:
            def __init__(self):
                self._name = "test"

            @property
            def name(self):
                return self._name

            @property
            def bad_prop(self):
                raise ValueError("Intentional error in property access")

        obj = ProblematicProperty()
        sj = SmartJson(obj)
        with self.assertRaisesRegex(SmartJsonSerializationError, "Error converting attributes for 'ProblematicProperty'"):
            sj.serialize()

    def test_serialization_error_for_vars_failure(self):
        # Tests the scenario where vars() fails on an object during _DataTypeConversion.
        class VarsFails:
            def __init__(self):
                self.a = 1 # Add an attribute to ensure it's not just an empty object issue

            @property
            def __dict__(self): # Override __dict__ to cause vars() to fail
                raise TypeError("Simulating vars() failure on this object")

        sj_vars_fails = SmartJson(VarsFails())
        # _DataTypeConversion.convert() catches exceptions from __convert_attributes (where vars() is called)
        # and wraps them in SmartJsonSerializationError.
        with self.assertRaisesRegex(SmartJsonSerializationError, "Error converting attributes for 'VarsFails'"):
            sj_vars_fails.serialize()

    # --- Schema Validation Tests ---

    # --- Deserialization Schema Validation Tests ---
    def test_deserialize_valid_schema_success(self):
        valid_user_json = json.dumps({
            'name': 'John Doe',
            'age': 30,
            'email': 'john.doe@example.com',
            'address': {'street': '123 Main St', 'city': 'Anytown', 'zip_code': '12345'},
            'roles': ['user', 'admin'],
            'items': [
                {'item_id': 1, 'price': 10.50},
                {'item_id': 2, 'price': 5.25}
            ]
        })
        sj = SmartJson()
        # Should not raise
        obj = sj.toObject(valid_user_json, schema=VALID_USER_SCHEMA)
        self.assertEqual(obj.name, 'John Doe') # _KObject access
        self.assertEqual(obj.address.city, 'Anytown')
        self.assertEqual(obj.items[0].item_id, 1)


    def test_deserialize_missing_required_field(self):
        invalid_json = json.dumps({'age': 30}) # 'name' is missing
        sj = SmartJson()
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, "Missing required field: 'name'"):
            sj.toObject(invalid_json, schema=VALID_USER_SCHEMA)

    def test_deserialize_incorrect_type(self):
        invalid_json = json.dumps({'name': 'Test', 'age': 'thirty'}) # age is str, expected int
        sj = SmartJson()
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, r"Invalid type for field 'age'. Expected 'int', got 'str'"):
            sj.toObject(invalid_json, schema=VALID_USER_SCHEMA)

    def test_deserialize_nested_missing_required_field(self):
        invalid_json = json.dumps({
            'name': 'Jane Doe',
            'age': 28,
            'address': {'street': '456 Oak Ln'} # 'city' and 'zip_code' missing from address
        })
        sj = SmartJson()
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, "Missing required field: 'address.city'"):
            sj.toObject(invalid_json, schema=VALID_USER_SCHEMA)

    def test_deserialize_nested_incorrect_type(self):
        invalid_json = json.dumps({
            'name': 'Jane Doe',
            'age': 28,
            'address': {'street': '456 Oak Ln', 'city': 12345, 'zip_code': '54321'} # city is int
        })
        sj = SmartJson()
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, r"Invalid type for field 'address.city'. Expected 'str', got 'int'"):
            sj.toObject(invalid_json, schema=VALID_USER_SCHEMA)

    def test_deserialize_list_item_incorrect_type(self):
        invalid_json = json.dumps({
            'name': 'List Test', 'age': 25,
            'roles': ['user', 123] # 123 is not a string
        })
        sj = SmartJson()
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, r"Invalid type for item at 'roles\[1\]'. Expected 'str', got 'int'"):
            sj.toObject(invalid_json, schema=VALID_USER_SCHEMA)

    def test_deserialize_list_item_incorrect_schema(self):
        invalid_json = json.dumps({
            'name': 'List Schema Test', 'age': 40,
            'items': [{'item_id': 1, 'price': 'cheap'}] # price is str, expected float
        })
        sj = SmartJson()
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, r"Invalid type for field 'items\[0\].price'. Expected 'float', got 'str'"):
            sj.toObject(invalid_json, schema=VALID_USER_SCHEMA)

    def test_deserialize_optional_field_absent(self):
        # 'email', 'address', 'roles', 'items' are optional
        valid_json_minimal = json.dumps({'name': 'Minimal User', 'age': 50})
        sj = SmartJson()
        obj = sj.toObject(valid_json_minimal, schema=VALID_USER_SCHEMA) # Should pass
        self.assertEqual(obj.name, "Minimal User")
        self.assertFalse(hasattr(obj, 'email')) # _KObject won't have it if not in JSON

    # --- Serialization Schema Validation Tests ---
    def test_serialize_valid_object_success(self):
        address = ValidAddress("789 Pine", "Otherville", "67890")
        items = [ValidItem(item_id=10, price=100.0)]
        user = ValidUser("Valid User", 40, email="valid@example.com", address=address, roles=["editor"], items=items)

        sj = SmartJson(user)
        # Should not raise
        serialized_json = sj.serialize(schema=VALID_USER_SCHEMA, pretty=False)
        # Basic check that serialization ran
        self.assertIn('"name": "Valid User"', serialized_json)
        self.assertIn('"street": "789 Pine"', serialized_json)
        self.assertIn('"item_id": 10', serialized_json)


    def test_serialize_missing_required_attribute(self):
        class UserMissingAge: # Helper class for this specific test
            def __init__(self, name):
                self.name = name

        user_obj = UserMissingAge("Test NoAge")
        sj = SmartJson(user_obj)
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, "Missing required attribute/key: 'age'"):
            sj.serialize(schema=VALID_USER_SCHEMA)

    def test_serialize_incorrect_attribute_type(self):
        user_obj = ValidUser("Test WrongAge", "thirty") # Age is str, schema expects int
        sj = SmartJson(user_obj)
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, r"Invalid type for attribute/key 'age'. Expected .*int.*, got str"):
            sj.serialize(schema=VALID_USER_SCHEMA)

    def test_serialize_nested_missing_attribute(self):
        class AddressMissingCity: # Helper class
            def __init__(self, street, zip_code):
                self.street = street
                self.zip_code = zip_code

        address = AddressMissingCity("123 Elm", "90210")
        user = ValidUser("Nested Test", 35, address=address)
        sj = SmartJson(user)
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, "Missing required attribute/key: 'address.city'"):
            sj.serialize(schema=VALID_USER_SCHEMA)

    def test_serialize_nested_incorrect_attribute_type(self):
        address = ValidAddress("Main St", 12345, "54321") # City is int, schema expects str
        user = ValidUser("Nested Type Test", 33, address=address)
        sj = SmartJson(user)
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, r"Invalid type for attribute/key 'address.city'. Expected .*str.*, got int"):
            sj.serialize(schema=VALID_USER_SCHEMA)

    def test_serialize_list_item_incorrect_type(self):
        user = ValidUser("List Type Test", 22, roles=['user', 123]) # 123 is not str
        sj = SmartJson(user)
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, r"Invalid type for item at 'roles\[1\]'. Expected .*str.*, got int"):
            sj.serialize(schema=VALID_USER_SCHEMA)

    def test_serialize_list_item_incorrect_schema(self):
        items = [ValidItem(1, "expensive")] # Price is str, schema expects float
        user = ValidUser("List Schema Test", 42, items=items)
        sj = SmartJson(user)
        with self.assertRaisesRegex(SmartJsonSchemaValidationError, r"Invalid type for attribute/key 'items\[0\].price'. Expected float, got str"):
            sj.serialize(schema=VALID_USER_SCHEMA)

    def test_serialize_optional_field_absent(self):
        user = ValidUser("Minimal User For Serialize", 55) # Optional fields (email, address, etc.) are absent
        sj = SmartJson(user)
        # Should pass without error
        serialized_data = sj.serialize(schema=VALID_USER_SCHEMA, pretty=False)
        self.assertIn('"name": "Minimal User For Serialize"', serialized_data)
        self.assertNotIn("email", serialized_data) # Ensure optional fields are not there if not set


    # --- Basic Serialization/Deserialization Tests ---
    def test_simple_object_serialization_deserialization(self):
        obj = SimpleObject("test_obj", 123)
        sj = SmartJson(obj)

        serialized_data = sj.serialize(pretty=False) # Test non-pretty version too
        # Expected: {"name": "test_obj", "value": 123} within the classname wrapper
        # e.g. {"SimpleObject": {"name": "test_obj", "value": 123}}

        # Check basic structure
        loaded_from_serialize = json.loads(serialized_data)
        self.assertIn(obj.__class__.__name__, loaded_from_serialize)
        self.assertEqual(loaded_from_serialize[obj.__class__.__name__]["name"], "test_obj")
        self.assertEqual(loaded_from_serialize[obj.__class__.__name__]["value"], 123)

        deserialized_obj = sj.toObject(serialized_data)
        self.assertIsInstance(deserialized_obj, SmartJson._KObject) # SmartJson wraps in _KObject
        # Accessing attributes from _KObject
        # The deserialized object's top level is the class name key
        kobject_inner = getattr(deserialized_obj, obj.__class__.__name__)

        self.assertEqual(kobject_inner.name, "test_obj")
        self.assertEqual(kobject_inner.value, 123)

    def test_object_with_list_serialization_deserialization(self):
        obj = ContainerObject("container_with_list")
        obj.list_attr.append(SimpleObject("item1", "alpha"))
        obj.list_attr.append(100)
        obj.list_attr.append(True)

        sj = SmartJson(obj)
        serialized_data = sj.serialize(pretty=False)

        deserialized_obj = sj.toObject(serialized_data)
        kobject_inner = getattr(deserialized_obj, obj.__class__.__name__)

        self.assertEqual(kobject_inner.name, "container_with_list")
        self.assertEqual(len(kobject_inner.list_attr), 3)
        # First item was SimpleObject, check its attributes
        self.assertEqual(kobject_inner.list_attr[0].name, "item1")
        self.assertEqual(kobject_inner.list_attr[0].value, "alpha")
        self.assertEqual(kobject_inner.list_attr[1], 100)
        self.assertEqual(kobject_inner.list_attr[2], True)


    def test_object_with_dict_serialization_deserialization(self):
        obj = ContainerObject("container_with_dict")
        obj.dict_attr["simple"] = SimpleObject("item_dict", "beta")
        obj.dict_attr["number"] = 200
        obj.dict_attr["boolean"] = False

        sj = SmartJson(obj)
        serialized_data = sj.serialize(pretty=False)

        deserialized_obj = sj.toObject(serialized_data)
        kobject_inner = getattr(deserialized_obj, obj.__class__.__name__)

        self.assertEqual(kobject_inner.name, "container_with_dict")
        self.assertIn("simple", kobject_inner.dict_attr)
        self.assertEqual(kobject_inner.dict_attr["simple"].name, "item_dict")
        self.assertEqual(kobject_inner.dict_attr["simple"].value, "beta")
        self.assertEqual(kobject_inner.dict_attr["number"], 200)
        self.assertEqual(kobject_inner.dict_attr["boolean"], False)

    def test_file_io_serialization_deserialization(self):
        test_dir = "tests"
        if not os.path.exists(test_dir):
            test_dir = "." # Fallback

        filename = os.path.join(test_dir, "test_file_io.json")

        original_obj = SimpleObject("file_test", 789)
        sj_writer = SmartJson(original_obj)

        try:
            sj_writer.serializeToJsonFile(directory=test_dir, filename="test_file_io.json")
            self.assertTrue(os.path.exists(filename))

            sj_reader = SmartJson() # Fresh SmartJson instance for reading
            deserialized_obj_k = sj_reader.toObjectFromFile(filename)

            # The structure from toObjectFromFile is directly the _KObject containing attributes
            # if the file was written with the classname as the top key.
            # SmartJson.serializeToJsonFile wraps with classname.
            deserialized_inner = getattr(deserialized_obj_k, original_obj.__class__.__name__)

            self.assertEqual(deserialized_inner.name, "file_test")
            self.assertEqual(deserialized_inner.value, 789)

        finally:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == '__main__':
    unittest.main()
