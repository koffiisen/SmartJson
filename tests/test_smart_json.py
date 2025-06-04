import unittest
import os
import json # For malformed JSON test
from scripts.__smart_json__ import (
    SmartJson,
    SmartJsonError,
    SmartJsonSerializationError,
    SmartJsonDeserializationError,
    SmartJsonUnsupportedTypeError,
    SmartJsonCircularDependencyError
)

# Helper classes for testing
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
        with self.assertRaisesRegex(SmartJsonDeserializationError, "Invalid JSON format in input string"):
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
            with open(temp_file_name, "w") as f:
                f.write(malformed_json_content)

            with self.assertRaisesRegex(SmartJsonDeserializationError, f"Invalid JSON format in file '{temp_file_name}'"):
                sj.toObjectFromFile(temp_file_name)
        finally:
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)

    def test_unsupported_type_from_enum_conversion(self):
        # This test checks if _EnumConversion correctly raises SmartJsonUnsupportedTypeError
        # when given a non-enum type.
        try:
            # Accessing internal class for a more direct unit test
            from scripts.__smart_json__ import SmartJson as SJ_Internal
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
