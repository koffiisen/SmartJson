[![PyPI version](https://badge.fury.io/py/smartjson.svg)](https://pypi.org/project/smartjson/1.0.0/)
# Tool to convert Class to Json and Json to Object ([SmartJson](https://github.com/koffiisen/SmartJson))

[SmartJson](https://github.com/koffiisen/SmartJson) is a simple tool to convert any class to JSON and convert json to Object.

# Usage

## Requirements

[Python 3](https://www.python.org/downloads/) must be installed.

## How to run
* use code from github or
* `pip install superjson`

## Parameters

* `cls`: Class you want to convert to json

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
from scripts.__smart_json__ import SmartJson

class Pull:
    def __init__(self):
        self.id = 2
        self.title = "Iam pull"
        self.author = "Joel O."
        self.subPull = Pull.SubPull()

    class SubPull:
        def __init__(self):
            self.subId = 3
            self.subTitle = "I am sub title"
            self.subAuthor = "OKJ."


class Jobs:
    def __init__(self):
        self.name = 'John'
        self.url = "5444"
        self.id = 1
        self.job = Jobs.Job()

    def name(self, set=None):
        if set != None:
            self.name = set

        return self.name

    class Job:
        def __init__(self):
            self.job_name = 'Test'
            self.job_url = "_blank"
            self.date = datetime.datetime.now()
            self.date2 = datetime.datetime.now()
            self.item = Jobs.Item()
            self.pull = Pull()

    class Item:
        def __init__(self):
            self.item_name = 'item 1'
            self.item_boof = datetime.datetime.now()
            self.mylist = [1, 2, 3]
            self.another = Jobs.Item.Another()

        class Another:
            def __init__(self):
                self.age = 26
                self.precision = 99.56
                self.ville = "Lille"
                self.meteo = Jobs.Item.Another.Meteo()

            class Meteo:
                def __init__(self):
                    self.pluie = True
                    self.complex = complex(12, 78)
                    self.tuple = [((1, 'a'), (2, 'b'))]
                    self.none = None

jb = Jobs()
smart_json = SmartJson(jb)

# Disable pretty print
serialize = smart_json.serialize(pretty=False)
print(serialize)

# Use pretty print
pretty = SmartJson(Jobs()).serialize()
print(pretty)

```

### Output: 
```json
{
  "id": 1,
  "job": {
    "date": "2019-09-30 13:57:36.340899",
    "date2": "2019-09-30 13:57:36.340899",
    "item": {
      "another": {
        "age": 26,
        "meteo": {
          "complex": "(12+78j)",
          "none": "",
          "pluie": true,
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
        "precision": 99.56,
        "ville": "Lille"
      },
      "item_boof": "2019-09-30 13:57:36.340899",
      "item_name": "item 1",
      "mylist": [
        1,
        2,
        3
      ]
    },
    "job_name": "Test",
    "job_url": "_blank",
    "pull": {
      "author": "Joel O.",
      "id": 2,
      "subPull": {
        "subAuthor": "OKJ.",
        "subId": 3,
        "subTitle": "I am sub title"
      },
      "title": "Iam pull"
    }
  },
  "name": "John",
  "url": "5444"
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

###Author : [Koffi Joel O.](https://github.com/koffiisen)


