# examples/01_basic_serialization_deserialization.py
from __future__ import print_function, unicode_literals, division, absolute_import
from smartjson import SmartJson
import datetime

print("### Basic Serialization and Deserialization Example ###")

# --- Basic Dictionary Serialization ---
print("\n--- Dictionary Serialization ---")
simple_dict = {
    "name": "John Doe",
    "age": 30,
    "city": "New York"
}
sj_dict = SmartJson(simple_dict)
json_from_dict = sj_dict.serialize()
print("Serialized JSON from Dictionary:")
print(json_from_dict)

# --- Basic Object Serialization ---
print("\n--- Object Serialization ---")
class SimpleUser:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.signup_date = datetime.date(2023, 1, 15)

user_instance = SimpleUser("Jane Smith", "jane.smith@example.com")
sj_user = SmartJson(user_instance)
json_from_user = sj_user.serialize()
print("\nSerialized JSON from SimpleUser Object:")
print(json_from_user) # Default class name 'SimpleUser' will be the key

# --- Basic Deserialization to SmartJson._KObject ---
print("\n--- Deserialization (JSON String to SmartJson._KObject) ---")
json_string = '{"title": "My Book", "author": "An Author", "published_year": 2024}'
sj_deserializer = SmartJson()
book_object = sj_deserializer.toObject(json_string)

print("Deserialized Object Type:", type(book_object))
print("Book Title:", book_object.title)
print("Book Author:", book_object.author)
print("Published Year:", book_object.published_year)

# --- Deserialization of a JSON with a list ---
print("\n--- Deserialization of JSON with a list ---")
json_with_list = '{"name": "Shopping List", "items": ["Milk", "Bread", "Eggs"]}'
shopping_list_obj = sj_deserializer.toObject(json_with_list)
print("List Name:", shopping_list_obj.name)
print("Items:", shopping_list_obj.items)
print("First item:", shopping_list_obj.items[0])
