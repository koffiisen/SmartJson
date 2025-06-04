[![PyPI version](https://badge.fury.io/py/smartjson.svg)](https://pypi.org/project/smartjson/)
[![PyPI version](https://img.shields.io/pypi/pyversions/smartjson.svg)](https://pypi.org/project/smartjson/)
[![PyPI version](https://img.shields.io/pypi/dm/smartjson.svg)](https://pypi.org/project/smartjson/)
[![CI](https://github.com/{{OWNER}}/{{REPOSITORY}}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{OWNER}}/{{REPOSITORY}}/actions/workflows/ci.yml)


[![PyPI install](https://img.shields.io/badge/Link-Install-blue.svg)](https://pypi.org/project/smartjson/)
[![PyPI version](https://img.shields.io/badge/Link-GitHub-blue.svg)](https://github.com/koffiisen/SmartJson)
[![PyPI download](https://img.shields.io/badge/Link-Download-blue.svg)](https://pypi.org/pypi/smartjson#files)

* ``BigQuery | Google cloud`` [<==>](https://cloud.google.com/bigquery/) 

[![Downloads](https://pepy.tech/badge/smartjson)](https://pepy.tech/project/smartjson)
[![Downloads](https://pepy.tech/badge/smartjson/month)](https://pepy.tech/project/smartjson/month)
[![Downloads](https://pepy.tech/badge/smartjson/week)](https://pepy.tech/project/smartjson/week)

### Python libraries to convert class to json, object and dict to Json and Json to Object ([SmartJson](https://github.com/koffiisen/SmartJson))

[SmartJson](https://github.com/koffiisen/SmartJson) is a simple tool to convert any class or dict to JSON and convert json to Object.

Documentation
===============================================================================
Features: 
## ``version (2.0.3) ``
* update list serialization

## ``version (2.0.2) ``
* Fix script
* Add script support enumeration (``enum``)
* Already support type : * ``class``
                         * ``date``
                         * ``datetime``
                         * ``set``
                         * ``OrderedDict``
                         * ``deque``
                         * ``list``
                         * ``int``
                         * ``float``
                         * ``bool``
                         * ``complex``
                         * ``tuple``
                         * ``str``
                         * ``dict``
                         * ``bytes``
                         * ``None``
* ### ex :
    ```python
  from enum import Enum, IntEnum
  from scripts import SmartJson
  
  class LoggerLevel(Enum):
      CRITICAL = 'CRITICAL'
      ERROR = 'ERROR'
      WARNING = 'WARNING'
      INFO = 'INFO'
      DEBUG = 'DEBUG'
      NOTSET = "NOTSET"
      
      
  class Status(IntEnum):
      success = 0
      failure = 1
  
  print(SmartJson({'Log': LoggerLevel, 'Stat': Status}).serialize())
    ```
* ### output :
  ```json

  {
    "Log": [
      {
        "CRITICAL": "CRITICAL",
        "DEBUG": "DEBUG",
        "ERROR": "ERROR",
        "INFO": "INFO",
        "NOTSET": "data",
        "WARNING": "WARNING"
      }
    ],
    "Stat": [
      {
        "failure": 1,
        "success": 0
      }
    ]
  }
  
   ```
        
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
address_schema = {
    'street': {'type': str, 'required': True}, # For serialization, type is str
                                               # For deserialization, type would be "str"
    'city': {'type': str, 'required': True}
}

# For deserialization, you'd typically use string type names:
address_schema_deserialization = {
    'street': {'type': "str", 'required': True},
    'city': {'type': "str", 'required': True},
    'zip_code': {'type': "str", 'required': True}
}

user_schema_serialization = {
    'name': {'type': str, 'required': True},
    'age': {'type': int, 'required': True},
    'is_active': {'type': bool, 'required': False},
    'address': {'type': Address, 'required': False, 'schema': address_schema}, # Validates 'address' attr is instance of Address, then validates its structure
    'tags': {'type': list, 'required': False, 'item_type': str}, # List of strings
    'items': {
        'type': list,
        'required': False,
        'item_type': dict, # Or a specific class like 'Item' for serialization
        'item_schema': { # Schema for each dictionary/object in the 'items' list
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
        'item_type': "dict", # Items are expected to be dictionaries
        'item_schema': { # Schema for each dictionary in the 'items' list
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
class User:
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


## ``version (2.0.1) ``
* Fix script
* update complex serialization
* Add new method ([`serializeToJsonFile`]()) ``convert your class to json file``
* [dict]() : ``Default parameter directory="output", filename="smart.json" ``
* [class]() : ``Default parameter directory="output", filename="className.json"``

* ### ex :
    - ``SmartJson(Test()).serializeToJsonFile(directory="yourPath", filename="MyFileName.json")``
    
    - ``SmartJson(Test()).serializeToJsonFile() :=> (output) :=> outpout/Test.json ``

## ``version (2.0.0) ``
**Support**  : 
* ``Class``
* ``date``
* ``datetime``
* ``set``
* ``OrderedDict``
* ``deque``
* ``list``
* ``int``
* ``float``
* ``bool``
* ``complex``
* ``tuple``
* ``str``
* ``dict``
* ``bytes``
* ``None``


 ``Install``
------------------------------------------------------------------------------

``smartjson`` is released on PyPI, so all you need is:

    $ pip install smartjson

To upgrade to latest version:

    $ pip install --upgrade smartjson


# Usage

## Requirements

[Python >= 2.7](https://www.python.org/downloads/) must be installed.

## Parameters

* `class or object or dict`:  you want to convert to json

## Project structure:

* `scripts` - source code of a package
* `example.py` - working examples

## Contribute

1. If unsure, open an issue for a discussion
1. Create a fork
1. Make your change
1. Make a pull request
1. Happy contribution!

## EXAMPLE

### Class

```python
import datetime
from collections import deque, OrderedDict
from scripts.__smart_json__ import SmartJson


class Test:
    def __init__(self):
        self.test = "none"
        self.id = 2
        self.date = datetime.datetime.now()
        self.tuple = [((1, 'a'), (2, 'b'))]


data = {
    "int": 1,
    "str": "SmartJson",
    "bytes": "pip install smartjson".encode("utf-8"),
    "date": datetime.date(2010, 1, 1),
    "datetime": datetime.datetime(2020, 1, 1, 18, 30, 0, 500),
    "pull": Test(),
    "set": (["1", 12, datetime.datetime.now()]),
    "list": [datetime.datetime.now(), Test()],
    "ordereddict": OrderedDict([
        ("b", OrderedDict([("b", Test()), ("a", datetime.datetime.now())])),
        ("a", OrderedDict([("b", 1), ("a", [((1, 'a'), (datetime.datetime.now(), 'b'))])])),
    ]),
    "deque": deque([
        deque([1, 2]),
        deque([3, 4]),
    ])
}


class Pull:
    def __init__(self):
        self.id = 2
        self.title = "Iam pull"
        self.author = "Joel O."
        self.subPull = Pull.SubPull()
        self.data = data
        self.date = datetime.datetime.now()
        self.list = [1, datetime.datetime.now(), Pull.SubPull()]

    class SubPull:
        def __init__(self):
            self.subId = 3
            self.subTitle = "I am sub title"
            self.subAuthor = "OKJ."
            self.date = datetime.date(2010, 1, 1)

# Example
my_json = SmartJson(data).serialize()
print(my_json)

```

### Output: 
```json
{
  "bytes": "pip install smartjson",
  "date": "2010-01-01",
  "datetime": "2020-01-01 18:30:00.000500",
  "deque": {
    "1": 2,
    "3": 4
  },
  "int": 1,
  "list": [
    "2019-10-01 19:39:01.916122",
    {
      "date": "2019-10-01 19:39:01.916122",
      "id": 2,
      "test": "none",
      "tuple": [
        [
          [
            1,
            "a"
          ],
          [
            2,
            "b"
          ]
        ]
      ]
    }
  ],
  "ordereddict": {
    "a": {
      "a": [
        [
          [
            1,
            "a"
          ],
          [
            "2019-10-01 19:39:01.916122",
            "b"
          ]
        ]
      ],
      "b": 1
    },
    "b": {
      "a": "2019-10-01 19:39:01.916122",
      "b": {
        "date": "2019-10-01 19:39:01.916122",
        "id": 2,
        "test": "none",
        "tuple": [
          [
            [
              1,
              "a"
            ],
            [
              2,
              "b"
            ]
          ]
        ]
      }
    }
  },
  "pull": {
    "date": "2019-10-01 19:39:01.916122",
    "id": 2,
    "test": "none",
    "tuple": [
      [
        [
          1,
          "a"
        ],
        [
          2,
          "b"
        ]
      ]
    ]
  },
  "set": [
    "1",
    12,
    "2019-10-01 19:39:01.916122"
  ],
  "str": "SmartJson"
}
```
### Json to Object
```text

objFromFile = smart_json.toObjectFromFile("jobs.json")
obj = smart_json.toObject('{"people":[{"name":"Scott", "website":"stackabuse.com", "from":"Nebraska"}]}')
obj2 = smart_json.toObject({'item': 'Beer', 'cost': '£4.00'})

print(obj2.item, obj2.cost)
print(objFromFile.job.item.another.precision)
print(obj.people[0].name, obj.people[0].website)

# Beer £4.00
# 99.56
# Scott stackabuse.com

```
### For support or coffee :)

[![screenshot](https://github.com/koffiisen/SmartJson/blob/master/bymecoffee.PNG?raw=true) ](https://www.paypal.me/smartjson)

## Author : [Koffi Joel O.](https://github.com/koffiisen)


