[![PyPI version](https://badge.fury.io/py/smartjson.svg)](https://pypi.org/project/smartjson/)
[![PyPI version](https://img.shields.io/pypi/pyversions/smartjson.svg)](https://pypi.org/project/smartjson/)
[![PyPI version](https://img.shields.io/pypi/dm/smartjson.svg)](https://pypi.org/project/smartjson/)


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


