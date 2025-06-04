# SmartJson - Seamless Python-JSON Data Interchange

[![PyPI version](https://badge.fury.io/py/smartjson.svg)](https://pypi.org/project/smartjson/)
[![PyPI license](https://img.shields.io/pypi/l/smartjson.svg)](LICENSE)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/smartjson.svg)](https://pypi.org/project/smartjson/)
[![PyPI dm](https://img.shields.io/pypi/dm/smartjson.svg)](https://pypi.org/project/smartjson/)
[![CI](https://github.com/{{OWNER}}/{{REPOSITORY}}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{OWNER}}/{{REPOSITORY}}/actions/workflows/ci.yml)
[![Downloads](https://pepy.tech/badge/smartjson)](https://pepy.tech/project/smartjson)
[![Downloads month](https://pepy.tech/badge/smartjson/month)](https://pepy.tech/project/smartjson/month)
[![Downloads week](https://pepy.tech/badge/smartjson/week)](https://pepy.tech/project/smartjson/week)

**Handy Links:**
<br>[![PyPI install](https://img.shields.io/badge/Link-Install-blue.svg)](https://pypi.org/project/smartjson/)
[![GitHub repo](https://img.shields.io/badge/Link-GitHub-blue.svg)](https://github.com/koffiisen/SmartJson)
[![PyPI download](https://img.shields.io/badge/Link-Download-blue.svg)](https://pypi.org/pypi/smartjson#files)

*Note: The CI badge above requires you to replace `{{OWNER}}` and `{{REPOSITORY}}` with your actual GitHub username/organization and repository name.*

## Overview

SmartJson is a Python library designed to simplify the conversion between Python objects/dictionaries and JSON data. Its core purpose is to provide an intuitive and flexible way to serialize complex Python data structures into JSON strings or files, and to deserialize JSON back into accessible Python objects.

Key benefits include ease of use for common scenarios, robust support for a wide range of Python data types (including datetime, Enum, OrderedDict, deque, complex numbers, and sets), optional schema validation for both serialization and deserialization to ensure data integrity, and compatibility with both Python 2.7 and Python 3.6+. Whether you're working with simple dictionaries or deeply nested custom objects, SmartJson aims to streamline your data interchange tasks.

## Features

*   **Versatile Serialization**: Serialize Python objects (custom classes, instances) and dictionaries to JSON strings.
*   **Flexible Deserialization**: Deserialize JSON strings and files into dynamic Python objects (`SmartJson._KObject`) that allow attribute-style access.
*   **Extensive Data Type Support**: Handles a wide array of Python types out-of-the-box (see "Supported Data Types" section below).
*   **Schema Validation**: Optional validation of data against a user-defined schema during both serialization (validating Python objects) and deserialization (validating incoming JSON data).
    *   Supports required fields, type checking, nested object schemas, and typed lists.
    *   Raises `SmartJsonSchemaValidationError` with detailed path information on failure.
*   **Nested Structures**: Seamlessly handles deeply nested objects and collections.
*   **Circular Dependency Detection**: Automatically detects and raises an error for circular references during serialization.
*   **Customizable JSON Output**: Supports pretty-printing for human-readable JSON.
*   **File I/O**: Convenience methods `serializeToJsonFile` and `toObjectFromFile` for working directly with JSON files (using UTF-8 encoding).
*   **Python 2 & 3 Compatibility**: Designed to work with Python 2.7 and Python 3.6+.

## Installation

Install `SmartJson` using pip:

```bash
pip install smartjson
```

To upgrade to the latest version:

```bash
pip install --upgrade smartjson
```
Dependencies like `six` (for Python 2/3 compatibility) and `enum34` (for Enum support in Python < 3.4 if you are using Python versions older than 3.4) will be automatically installed.

## Quick Start

This example provides a brief overview of serializing a Python object to JSON and deserializing a JSON string back into a Python object.

```python
from __future__ import print_function, unicode_literals # For Py2/3 print & string compatibility
import datetime
from smartjson import SmartJson

# --- Define a simple class ---
class Product:
    def __init__(self, name, price, available_since):
        self.name = name
        self.price = price
        self.available_since = available_since # A datetime.date object

# --- Serialization ---
# Create an instance of our class
product_instance = Product("Awesome Laptop", 999.99, datetime.date(2023, 10, 26))

# Create a SmartJson instance with the object to serialize
sj_serializer = SmartJson(product_instance)

# Serialize the object to a pretty JSON string
product_json = sj_serializer.serialize(pretty=True)

print("--- Serialized Product ---")
print(product_json)
# Expected output will be something like:
# {
#   "Product": {
#     "available_since": "2023-10-26",
#     "name": "Awesome Laptop",
#     "price": 999.99
#   }
# }

# --- Deserialization ---
# A simple JSON string representing a store
store_json_string = '''
{
    "store_name": "Main Street Electronics",
    "location": "123 Main St",
    "inventory_count": 1500
}
'''

# Create an empty SmartJson instance for deserialization
sj_deserializer = SmartJson()

# Deserialize the JSON string
store_obj = sj_deserializer.toObject(store_json_string)

print("\n--- Deserialized Store ---")
print("Store Name: {}".format(store_obj.store_name))
print("Location: {}".format(store_obj.location))
print("Inventory Count: {}".format(store_obj.inventory_count))
# The deserialized object allows attribute-style access.
```

For more detailed examples, including handling various data types, nested structures, schema validation, and file operations, please refer to the scripts in the `examples/` directory.

## Core Concepts & Usage

### 7.1. Initialization

How you initialize `SmartJson` depends on whether you're primarily serializing or deserializing.

*   **For Serialization**:
    Pass the Python object (custom class instance, dictionary, list, or other supported type) to the `SmartJson` constructor.
    ```python
    my_object = {"key": "value", "number": 123}
    # or
    # class MyClass:
    #   def __init__(self): self.data = "sample"
    # my_object = MyClass()

    sj_for_serialization = SmartJson(my_object)
    ```

*   **For Deserialization**:
    You can create an empty `SmartJson` instance and then use its `toObject()` or `toObjectFromFile()` methods.
    ```python
    sj_for_deserialization = SmartJson()
    # Then call:
    # python_obj = sj_for_deserialization.toObject(json_string)
    # or
    # python_obj = sj_for_deserialization.toObjectFromFile("data.json")
    ```

### 7.2. Serialization

To convert a Python object (that you passed to the constructor) into a JSON string, use the `serialize()` method.

```python
# Assuming sj_for_serialization = SmartJson(my_object) from above

# Serialize to a compact JSON string
json_string_compact = sj_for_serialization.serialize(pretty=False)

# Serialize to a pretty-printed (indented) JSON string
json_string_pretty = sj_for_serialization.serialize(pretty=True) # pretty=True is the default
print(json_string_pretty)
```
If the serialized object is an instance of a class, the resulting JSON will typically have the class name as the top-level key, with the object's attributes as a nested JSON object. For dictionaries and lists, they are serialized directly.

**Example: Serializing a Dictionary**
```python
data_dict = {"item": "Example", "value": 42, "active": True}
sj = SmartJson(data_dict)
print(sj.serialize())
# Output:
# {
#   "active": true,
#   "item": "Example",
#   "value": 42
# }
```

### 7.3. Deserialization

To convert a JSON string or a Python dictionary (parsed from JSON) into a Python object, use the `toObject()` method.

```python
json_data_string = '{"name": "Gadget", "id": "XG-100", "details": {"color": "blue", "weight_kg": 0.5}}'
sj = SmartJson() # Empty instance
product_obj = sj.toObject(json_data_string)

# Access data using attribute style
print(product_obj.name)       # Output: Gadget
print(product_obj.id)         # Output: XG-100
print(product_obj.details.color) # Output: blue
```
The `toObject()` method (and `toObjectFromFile()`) returns an instance of `SmartJson._KObject` (or a list of them if the JSON string represents a list). This special object allows you to access the JSON data using attribute-style access (e.g., `my_obj.key`) for keys that are valid Python identifiers.

### 7.4. Schema Validation (Brief)

`SmartJson` supports validating data structures against a schema for both serialization and deserialization. This is a powerful feature to ensure data integrity.

*   **Defining a Schema**: Schemas are dictionaries defining expected fields, types, and constraints.
    ```python
    # Example for serializing a Point object
    # point_schema_serialization = {'x': {'type': int, 'required': True}, 'y': {'type': int, 'required': True}}

    # Example for deserializing JSON to a point-like structure
    # point_schema_deserialization = {'x': {'type': "int", 'required': True}, 'y': {'type': "int", 'required': True}}
    ```
    *(See the "Schema Validation" section below for a detailed explanation of schema definitions.)*

*   **Using with Serialization**:
    ```python
    # my_point_object = Point(10, 20)
    # serialized_point = SmartJson(my_point_object).serialize(schema=point_schema_serialization)
    ```
*   **Using with Deserialization**:
    ```python
    # point_json_str = '{"x": 10, "y": 20}'
    # point_data = SmartJson().toObject(point_json_str, schema=point_schema_deserialization)
    ```
If validation fails, `SmartJsonSchemaValidationError` is raised. For a full explanation and detailed examples of schema definition and usage, please see the **Schema Validation** section below and the example script: [`examples/03_schema_validation_demo.py`](examples/03_schema_validation_demo.py).

### 7.5. Working with Files

`SmartJson` provides convenience methods to serialize objects directly to JSON files and deserialize JSON files back into Python objects.

*   **Serializing to a File**: `serializeToJsonFile()`
    ```python
    # my_data can be a dictionary, list, or custom object instance
    # SmartJson(my_data).serializeToJsonFile(directory="output_data", filename="my_output.json")
    ```
    This will create `my_output.json` in the `output_data` directory.

*   **Deserializing from a File**: `toObjectFromFile()`
    ```python
    # loaded_data = SmartJson().toObjectFromFile("output_data/my_output.json")
    # print(loaded_data.some_attribute)
    ```
Both methods also accept the `schema` parameter for validation. For more examples, see [`examples/04_file_operations.py`](examples/04_file_operations.py).

## Supported Data Types

SmartJson is designed to handle a wide range of Python data types for both serialization and deserialization:

*   **Standard Types**:
    *   `dict` (including nested dictionaries)
    *   `list`, `tuple` (tuples are typically serialized as JSON arrays/lists)
    *   `str` (Python 3 Unicode strings, Python 2 `unicode`)
    *   `int` (Python 3 integers, Python 2 `int` and `long`)
    *   `float`
    *   `bool`
    *   `None` (serialized as JSON `null`)
*   **Date and Time**:
    *   `datetime.datetime` (serialized to ISO 8601 string format)
    *   `datetime.date` (serialized to ISO 8601 string format)
*   **Specialized Collections**:
    *   `collections.OrderedDict`
    *   `collections.deque` (serialized based on its content)
    *   `set` (serialized as a JSON array/list)
*   **Numeric Types**:
    *   `complex` numbers
*   **Enumerations**:
    *   `enum.Enum` and `enum.IntEnum` (serialized to their values). Requires the `enum34` package for Python versions older than 3.4.
*   **Binary Data**:
    *   `bytes` (decoded to UTF-8 strings during serialization).
*   **Custom Class Instances**:
    *   Instances of user-defined classes are serialized by converting their attributes.
    *   Deserialized JSON objects become instances of `SmartJson._KObject`, providing attribute-style access.

## Schema Validation

SmartJson now supports schema validation for both serialization and deserialization processes. This allows you to ensure that your Python objects (before serialization) or your JSON data (before deserialization) conform to a predefined structure and type constraints.

If validation fails, a `SmartJsonSchemaValidationError` is raised, providing a detailed message about the field or attribute that caused the failure, including its path.

### Defining Schemas

A schema is defined as a Python dictionary. Each key in the schema represents a field name (for dictionaries/JSON objects) or an attribute name (for Python objects). The value associated with each key is another dictionary specifying the properties for that field/attribute.

Supported properties in a field's schema definition:

*   `'type'`: (Required for type checking)
    *   When validating data for **deserialization** (from JSON), this should be a string name of the expected type after JSON parsing (e.g., `"str"`, `"int"`, `"float"`, `"bool"`, `"list"`, `"dict"`).
    *   When validating a Python object for **serialization**, this should be the actual Python type or class (e.g., `str`, `int`, `float`, `bool`, `list`, `dict`, or a custom class like `User`).
*   `'required'`: (Optional) A boolean indicating if the field/attribute is mandatory. Defaults to `False`.
*   `'schema'`: (Optional) For fields of type `dict` (deserialization) or fields that are objects/dictionaries (serialization), this property can hold a nested schema dictionary to validate the structure of the nested object/dictionary.
*   `'item_type'`: (Optional) For fields of type `list`, this specifies the expected type of items within the list.
    *   For deserialization, use type names: `"str"`, `"int"`, etc.
    *   For serialization, use Python types: `str`, `int`, etc.
*   `'item_schema'`: (Optional) For fields of type `list` where items are expected to be objects/dictionaries, this provides a schema definition for each item in the list.

**Example Schema Definition:**

```python
# For Python classes (used in serialization validation or as type hints)
class Address:
    pass # Define attributes as needed

class User:
    pass # Define attributes as needed

# Schema definition
address_schema_serialization = { # For serializing Address objects
    'street': {'type': str, 'required': True},
    'city': {'type': str, 'required': True}
}

address_schema_deserialization = { # For deserializing JSON into an address-like structure
    'street': {'type': "str", 'required': True},
    'city': {'type': "str", 'required': True},
    'zip_code': {'type': "str", 'required': True}
}

user_schema_serialization = {
    'name': {'type': str, 'required': True},
    'age': {'type': int, 'required': True},
    'is_active': {'type': bool, 'required': False},
    'address': {'type': Address, 'required': False, 'schema': address_schema_serialization},
    'tags': {'type': list, 'required': False, 'item_type': str},
    'items': {
        'type': list,
        'required': False,
        'item_type': dict, # Or a specific class like 'Item' if items are instances
        'item_schema': {
            'item_id': {'type': int, 'required': True},
            'description': {'type': str}
        }
    }
}

user_schema_deserialization = {
    'name': {'type': "str", 'required': True},
    'age': {'type': "int", 'required': True},
    'is_active': {'type': "bool", 'required': False},
    'address': {'type': "dict", 'required': False, 'schema': address_schema_deserialization},
    'tags': {'type': "list", 'required': False, 'item_type': "str"},
    'items': {
        'type': "list",
        'required': False,
        'item_type': "dict",
        'item_schema': {
            'item_id': {'type': "int", 'required': True},
            'description': {'type': "str"}
        }
    }
}
```
**Note:** For deserialization (`_validate_data`), the `'type'` and `'item_type'` in the schema should be strings like `"str"`, `"int"`, `"list"`, `"dict"`. For serialization (`_validate_object`), these should be actual Python types/classes like `str`, `int`, `list`, `dict`, `MyCustomClass`.

### Using Schemas

**For Deserialization:**
Pass the schema to `toObject` or `toObjectFromFile`:
```python
from smartjson import SmartJson, SmartJsonSchemaValidationError

# Assume user_schema_deserialization is defined as above
json_string = '{"name": "Alice", "age": "thirty"}' # Age is incorrect type
sj = SmartJson()

try:
    user_obj = sj.toObject(json_string, schema=user_schema_deserialization)
except SmartJsonSchemaValidationError as e:
    print(f"Schema validation failed: {e}")
    # Expected output: Schema validation failed: Invalid type for field 'age'. Expected 'int', got 'str'.

# Similarly for toObjectFromFile:
# user_obj = sj.toObjectFromFile("user.json", schema=user_schema_deserialization)
```

**For Serialization:**
Pass the schema to `serialize` or `serializeToJsonFile`:
```python
# Assume User class and user_schema_serialization are defined
class User: # Simplified User class for example
    def __init__(self, name, age, is_active=None, address=None, tags=None, items=None):
        self.name = name
        self.age = age
        self.is_active = is_active
        self.address = address
        self.tags = tags
        self.items = items

user_instance = User(name="Bob", age="invalid_age") # Age should be int

sj = SmartJson(user_instance)
try:
    json_output = sj.serialize(schema=user_schema_serialization)
except SmartJsonSchemaValidationError as e:
    print(f"Schema validation failed during serialization: {e}")
    # Expected output: Schema validation failed during serialization: Invalid type for attribute/key 'age'. Expected int, got str.

# Similarly for serializeToJsonFile:
# sj.serializeToJsonFile(schema=user_schema_serialization)
```

If validation fails, a `SmartJsonSchemaValidationError` is raised, with a message indicating the path to the problematic field or attribute (e.g., `address.city` or `items[0].item_id`).

# Detailed Examples

The `examples/` directory contains scripts demonstrating various features of SmartJson:

-   **[`examples/01_basic_serialization_deserialization.py`](examples/01_basic_serialization_deserialization.py)**: Covers fundamental serialization of Python dictionaries/objects and deserialization of JSON.
-   **[`examples/02_nested_data_and_types.py`](examples/02_nested_data_and_types.py)**: Shows handling of complex structures like nested objects, lists, and various Python data types.
-   **[`examples/03_schema_validation_demo.py`](examples/03_schema_validation_demo.py)**: A focused guide on defining and using schemas for data validation.
-   **[`examples/04_file_operations.py`](examples/04_file_operations.py)**: Illustrates saving objects to JSON files and loading them back.

You can run these examples directly to see `SmartJson` in action.

## Requirements

[Python >= 2.7](https://www.python.org/downloads/) (Python 3.6+ recommended). Dependencies like `six` and `enum34` (for Python < 3.4) are handled by `pip install`.

## Project structure:

* `smartjson` - source code of the package
* `examples/` - directory with detailed example scripts
* `tests/` - unit tests
* `example.py` - a very basic quick start script

## Contribute

1. If unsure, open an issue for a discussion
1. Create a fork
1. Make your change
1. Make a pull request
1. Happy contribution!

### For support or coffee :)

[![screenshot](https://github.com/koffiisen/SmartJson/blob/master/bymecoffee.PNG?raw=true) ](https://www.paypal.me/smartjson)

## Author : [Koffi Joel O.](https://github.com/koffiisen)
