# examples/03_schema_validation_demo.py
from __future__ import print_function, unicode_literals, division, absolute_import
from smartjson import SmartJson
from smartjson.core import SmartJsonSchemaValidationError # For catching the specific error
import six # For types in schema if needed for Py2/3 consistency in definition

print("### Schema Validation Demo ###")

# --- Define Schemas ---

# Schemas for Deserialization (using string type names)
address_schema_deserialization = {
    'street': {'type': "str", 'required': True},
    'city': {'type': "str", 'required': True},
    'zip_code': {'type': "str", 'required': False}
}

user_schema_deserialization = {
    'username': {'type': "str", 'required': True},
    'email': {'type': "str", 'required': True},
    'age': {'type': "int", 'required': False},
    'address': {'type': "dict", 'required': False, 'schema': address_schema_deserialization},
    'roles': {'type': "list", 'required': False, 'item_type': "str"}
}

# --- Python Class Definitions (for serialization example) ---
class Address:
    def __init__(self, street, city, zip_code=None):
        self.street = street
        self.city = city
        if zip_code:
            self.zip_code = zip_code

class User:
    def __init__(self, username, email, age=None, address_obj=None, roles=None):
        self.username = username
        self.email = email
        if age is not None:
            self.age = age
        if address_obj:
            self.address = address_obj
        if roles:
            self.roles = roles

# Schemas for Serialization (using Python types)
# Note: For custom classes like 'Address', the 'type' is the class itself.
# The 'schema' entry for 'address' will then validate the attributes of the Address instance.
address_schema_serialization = {
    'street': {'type': six.string_types, 'required': True},
    'city': {'type': six.string_types, 'required': True},
    'zip_code': {'type': six.string_types, 'required': False}
}

user_schema_serialization = {
    'username': {'type': six.string_types, 'required': True},
    'email': {'type': six.string_types, 'required': True},
    'age': {'type': six.integer_types, 'required': False},
    'address': {'type': Address, 'required': False, 'schema': address_schema_serialization},
    'roles': {'type': list, 'required': False, 'item_type': six.string_types}
}


# --- Deserialization with Schema Validation ---
print("\n--- Deserialization Validation ---")
sj = SmartJson()

# Valid JSON
valid_user_json = '''
{
    "username": "johndoe",
    "email": "john.doe@example.com",
    "age": 30,
    "address": {
        "street": "123 Main St",
        "city": "Anytown"
    },
    "roles": ["user", "editor"]
}
'''
print("Attempting to deserialize valid user JSON...")
try:
    user_obj_valid = sj.toObject(valid_user_json, schema=user_schema_deserialization)
    print("Successfully deserialized valid user:", user_obj_valid.username)
    if hasattr(user_obj_valid, 'address'):
        print("User's street:", user_obj_valid.address.street)
except SmartJsonSchemaValidationError as e:
    print("Error deserializing valid user:", e)

# Invalid JSON - missing required field 'email'
invalid_user_json_missing_field = '''
{
    "username": "janedoe",
    "address": {
        "street": "456 Oak Rd",
        "city": "Otherville"
    }
}
'''
print("\nAttempting to deserialize user JSON with missing 'email'...")
try:
    sj.toObject(invalid_user_json_missing_field, schema=user_schema_deserialization)
except SmartJsonSchemaValidationError as e:
    print("Caught expected error:", e)

# Invalid JSON - incorrect type for 'age'
invalid_user_json_wrong_type = '''
{
    "username": "err_user",
    "email": "err@example.com",
    "age": "thirty"
}
'''
print("\nAttempting to deserialize user JSON with 'age' as string (should be int)...")
try:
    sj.toObject(invalid_user_json_wrong_type, schema=user_schema_deserialization)
except SmartJsonSchemaValidationError as e:
    print("Caught expected error:", e)

# Invalid JSON - incorrect type in list items
invalid_user_json_wrong_list_item_type = '''
{
    "username": "list_user",
    "email": "list@example.com",
    "roles": ["user", 123]
}
'''
print("\nAttempting to deserialize user JSON with 'roles' list having an int (should be strings)...")
try:
    sj.toObject(invalid_user_json_wrong_list_item_type, schema=user_schema_deserialization)
except SmartJsonSchemaValidationError as e:
    print("Caught expected error:", e)


# --- Serialization with Schema Validation ---
print("\n\n--- Serialization Validation ---")

# Valid Python object
valid_address_obj = Address(street="789 Pine Ln", city="Villagetown", zip_code="12345")
valid_user_obj = User(username="py_user", email="py@example.com", age=25, address_obj=valid_address_obj, roles=["admin"])

print("Attempting to serialize valid Python User object...")
try:
    json_output = SmartJson(valid_user_obj).serialize(schema=user_schema_serialization, pretty=True)
    print("Successfully serialized valid user object:")
    print(json_output)
except SmartJsonSchemaValidationError as e:
    print("Error serializing valid object:", e)

# Invalid Python object - missing required 'email' attribute
class UserMissingEmail:
    def __init__(self, username):
        self.username = username
invalid_user_obj_missing_attr = UserMissingEmail("no_email_user")

print("\nAttempting to serialize Python User object missing 'email' attribute...")
sj_invalid_attr = SmartJson(invalid_user_obj_missing_attr)
try:
    sj_invalid_attr.serialize(schema=user_schema_serialization)
except SmartJsonSchemaValidationError as e:
    print("Caught expected error:", e)

# Invalid Python object - 'age' attribute has wrong type
invalid_user_obj_wrong_type = User(username="type_err_user", email="type@example.com", age="young") # age is string

print("\nAttempting to serialize Python User object with 'age' as string...")
sj_invalid_type = SmartJson(invalid_user_obj_wrong_type)
try:
    sj_invalid_type.serialize(schema=user_schema_serialization)
except SmartJsonSchemaValidationError as e:
    print("Caught expected error:", e)
