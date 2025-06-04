# examples/02_nested_data_and_types.py
from __future__ import print_function, unicode_literals, division, absolute_import
from smartjson import SmartJson
import datetime
from collections import OrderedDict, deque
from enum import Enum

print("### Nested Data Structures and Various Types Example ###")

class Author:
    def __init__(self, name, birth_year):
        self.name = name
        self.birth_year = birth_year

class Book:
    def __init__(self, title, published_date, author_obj, tags_list, metadata_dict):
        self.title = title
        self.published_date = published_date
        self.author = author_obj # Nested object
        self.tags = tags_list     # List of strings
        self.metadata = metadata_dict # Dictionary

# Create instances
author_obj = Author("George Orwell", 1903)
book_obj = Book(
    title="1984",
    published_date=datetime.date(1949, 6, 8),
    author_obj=author_obj,
    tags_list=["dystopian", "sci-fi", "classic"],
    metadata_dict={
        "pages": 328,
        "rating": 4.5,
        "is_bestseller": True,
        "series": None,
        "formats": ("paperback", "ebook", "audiobook"), # tuple
        "related_ids": {101, 102} # set
    }
)

print("\n--- Original Book Object (Conceptual) ---")
# Using direct attribute access; f-strings for Py3.6+ or use .format for older
try:
    print("Title: {}".format(book_obj.title))
    print("Author: {}".format(book_obj.author.name))
    print("Tags: {}".format(book_obj.tags))
    print("Metadata Pages: {}".format(book_obj.metadata['pages']))
except AttributeError: # Fallback for older Python versions without f-string in __repr__
    print("Title:", book_obj.title)


# Serialize the complex Book object
sj_book = SmartJson(book_obj)
serialized_book_json = sj_book.serialize(pretty=True)

print("\n--- Serialized JSON for Book Object ---")
print(serialized_book_json)

# Deserialize it back
sj_deserializer = SmartJson()
deserialized_book = sj_deserializer.toObject(serialized_book_json) # Note: This deserializes to _KObject by default

print("\n--- Deserialized Book Object (as SmartJson._KObject) ---")
# The deserialized object will have the class name 'Book' as a top-level key
# and its attributes as nested _KObject instances or basic types.
book_data = deserialized_book.Book # Accessing the data under the 'Book' key

print("Title:", book_data.title)
print("Author Name (from nested object):", book_data.author.name)
print("First Tag:", book_data.tags[0])
print("Metadata Pages (from nested dict):", book_data.metadata.pages)
print("Metadata Formats (tuple becomes list):", book_data.metadata.formats) # Tuples are converted to lists in JSON
print("Metadata Related IDs (set becomes list):", book_data.metadata.related_ids) # Sets are converted to lists in JSON


# --- Example with Enum and other collection types ---
class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

data_with_collections = {
    "id": 123,
    "current_status": Status.ACTIVE, # Enum member
    "history_log": deque(["event1", "event2", "event3"]),
    "config": OrderedDict([("priority", 1), ("retries", 3)])
}

sj_collections = SmartJson(data_with_collections)
serialized_collections_json = sj_collections.serialize(pretty=True)

print("\n--- Serialized JSON for Data with Collections (including Enum) ---")
print(serialized_collections_json)

deserialized_collections = sj_deserializer.toObject(serialized_collections_json)
print("\n--- Deserialized Data with Collections ---")
print("ID:", deserialized_collections.id)
# Enum is serialized to its value
print("Current Status (Enum value):", deserialized_collections.current_status)
# Deque is serialized based on its internal structure (often as a list or dict if from items)
# The default _convert_value for deque converts it to OrderedDict then serializes the dict.
# If it was a simple deque(['a', 'b']), _convert_value would make it OrderedDict([(0,'a'), (1,'b')])
# Let's check actual output:
# For deque(["event1", "event2", "event3"]), _convert_value -> OrderedDict([(0,"event1"), (1,"event2"), (2,"event3")])
# This then becomes a dict in JSON: {"0": "event1", "1": "event2", "2": "event3"}
print("History Log (Deque becomes dict):", deserialized_collections.history_log)
print("Config (OrderedDict first key-value):", deserialized_collections.config.priority)
