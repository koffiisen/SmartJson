import os
from collections import OrderedDict, deque
from datetime import datetime, date

from scripts import SmartJson


class Test:
    def __init__(self):
        self.name = "test"
        self.date = datetime.now()
        self.list = ["is list item", 1, datetime.now()]
        self.complex = complex(2, -3)
        self.bytes = "Me".encode("utf-8")
        self.dict = {'url': "https://pypi.org/project/smartjson/", 'version': "2.0.0", 'author': "K.J.O",
                     'date': date(2019, 10, 1)}
        self.bool = True
        self.float = 9500.50
        self.int = 12
        self.path = os.getcwd()
        self.bytes = "pip install smartjson".encode("utf-8")


class MyObject:
    def __init__(self):
        self.object = Test()
        self.date = datetime.now()
        self.id = 1
        self.lastId = None
        self.set = (["1", 12, datetime.now()])
        self.list = [datetime.now(), 1]
        self.ordereddict = OrderedDict([
            ("b", OrderedDict([("b", 2), ("a", datetime.now())])),
            ("a", OrderedDict([("b", 1), ("a", [((1, 'a'), (datetime.now(), 'b'))])]))
        ])
        self.deque = deque([
            deque([1, 2]),
            deque([3, 4]),
        ])
        # self.data = data


data = {
    "int": 1,
    "str": "SmartJson",
    "bytes": "pip install smartjson".encode("utf-8"),
    "date": date(2010, 1, 1),
    "datetime": datetime(2020, 1, 1, 18, 30, 0, 500),
    "pull": Test(),
    "set": (["1", 12, datetime.now()]),
    "list": [datetime.now(), Test()],
    "ordereddict": OrderedDict([
        ("b", OrderedDict([("b", Test()), ("a", datetime.now())])),
        ("a", OrderedDict([("b", 1), ("a", [((1, 'a'), (datetime.now(), 'b'))])])),
    ]),
    "deque": deque([
        deque([1, 2]),
        deque([3, 4]),
    ]),
    'complex': complex(42, 13)
}

if __name__ == '__main__':
    print("")
    print(SmartJson(Test()).serialize())
    SmartJson(Test()).serializeToJsonFile()
    # * dict : Default parameter directory="SmartJSON", filename="smart.json"
    # * class : Default parameter directory="SmartJSON", filename="className.json"
    SmartJson(Test()).serializeToJsonFile(directory="yourPath", filename="MyFileName.json")

"""
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


class Jobs:
    def __init__(self):
        self.name = 'John'
        self.url = "5444"
        self.id = 1
        self.job = Jobs.Job()
        self.data = {
            "int": 1,
            "str": "SmartJson",
            "bytes": "pip install smartjson".encode("utf-8"),
            "date": datetime.date(2010, 1, 1)
        }

    def name(self, set=None):
        if set != None:
            self.name = set

        return self.name

    class Job:
        def __init__(self):
            self.job_name = 'Test'
            self.job_url = "_blank"
            self.date = datetime.datetime.now().strftime('%m/%d/%Y')
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


# print(SuperJSON(data).serialize())
my_json = SmartJson(Jobs()).serialize()
print(my_json)
# print("Hello".encode("utf-8"))

jb = Jobs()
super_json = SuperJSON(jb)
serialize = super_json.serialize(pretty=False)
print(serialize)

pretty = SuperJSON(Jobs()).serialize()
print(pretty)

objFromFile = super_json.toObjectFromFile("jobs.json")
obj = super_json.toObject('{"people":[{"name":"Scott", "website":"stackabuse.com", "from":"Nebraska"}]}')
obj2 = super_json.toObject({'item': 'Beer', 'cost': '£4.00', 'date': '02/23/2012'})

print(obj2.item, obj2.cost, obj2.date, type(obj2.date))
print(objFromFile.job.item.another.precision)
print(obj.people[0].name, obj.people[0].website)

print(type(objFromFile.job.date), objFromFile.job.date)
print(type(objFromFile.id))


def __iterate(cls):
    for attr, value in vars(cls).items():
        if hasattr(value, "__class__"):
            if isinstance(value, int) \
                    or isinstance(value, float) or isinstance(value, bool) \
                    or isinstance(value, complex) or isinstance(value, list) \
                    or isinstance(value, tuple) or isinstance(value, str) \
                    or isinstance(value, type(None)):
                print(attr, " = ", value)
            else:
                #print(attr, " = ", value.__dict__)
                __iterate(value)


__iterate(jb)
"""
