# example.py
from __future__ import print_function, unicode_literals, division, absolute_import
from smartjson import SmartJson
import datetime

# A simple class to demonstrate basic serialization
class QuickStartUser:
    def __init__(self, name, user_id, creation_time):
        self.name = name
        self.user_id = user_id
        self.is_active = True
        self.creation_time = creation_time

if __name__ == '__main__':
    print("### SmartJson Quick Start Example ###")

    # 1. Basic Object Serialization
    print("\n--- Serializing a Python Object ---")
    user = QuickStartUser("Alex", 101, datetime.datetime.now())
    smart_json_instance_user = SmartJson(user)
    user_json_string = smart_json_instance_user.serialize(pretty=True)

    print("Serialized User Object:")
    print(user_json_string)

    # 2. Basic Dictionary Serialization
    print("\n--- Serializing a Python Dictionary ---")
    sample_data = {
        "project_name": "SmartJson Demo",
        "version": "1.0",
        "supported_features": ["serialization", "deserialization", "schema_validation"]
    }
    smart_json_instance_dict = SmartJson(sample_data)
    dict_json_string = smart_json_instance_dict.serialize(pretty=True)

    print("Serialized Dictionary:")
    print(dict_json_string)

    # 3. Basic Deserialization (JSON string to SmartJson._KObject)
    print("\n--- Deserializing a JSON String ---")
    product_json = '''
    {
        "product_id": "P123",
        "name": "Awesome Gadget",
        "price": 99.99,
        "tags": ["electronics", "cool"]
    }
    '''
    sj_deserializer = SmartJson() # Create an empty instance for deserialization
    product_obj = sj_deserializer.toObject(product_json)

    print("Deserialized Product (as SmartJson._KObject):")
    # Using .format for Python 2 compatibility in this example script
    print("Product Name: {}".format(product_obj.name))
    print("Price: {}".format(product_obj.price))
    print("First Tag: {}".format(product_obj.tags[0]))

    print("\nFor more detailed examples, please see the scripts in the 'examples/' directory.")
    print("These include demonstrations of:")
    print("- Nested data structures and various data types")
    print("- Schema validation for serialization and deserialization")
    print("- File operations (saving to and loading from JSON files)")
    print("- And more basic use cases.")
