"""
Author : J. Koffi ONIPOH
Version : 2.0.1
email: jolli644@gmail.com
"""

import datetime
import json
import os
from collections import OrderedDict, deque
from copy import deepcopy


class SmartJson:
    def __init__(self, cls=None):
        """
        :param cls:
        """

        self.__copy = cls
        self.__classe = deepcopy(cls)
        self.___obj = None
        if cls:
            self.classname = cls.__class__.__name__

    def serialize(self, pretty=True):
        """
        :param pretty:
        :return:
        """
        try:
            if isinstance(self.__classe, dict):
                return SmartJson._DictConversion(self.__classe).serialize(pretty)
            elif isinstance(self.__classe, object):
                self.___obj = SmartJson._DataTypeConversion(self.__classe).next()
                if pretty:
                    return json.dumps({'' + self.classname: self._serialize(self.___obj).__dict__}, indent=2,
                                      sort_keys=True)
                else:
                    return json.dumps({'' + self.classname: self._serialize(self.___obj).__dict__}, sort_keys=True)


        except TypeError as e:
            SmartJson._UnsupportedClass((type(self.___obj).__name__), e)

    def serializeToJsonFile(self, directory="outpout", filename="smart.json"):
        """
        :param pretty:
        :return:
        """

        try:
            os.makedirs(directory)
        except OSError:
            if not os.path.isdir(directory):
                raise

        try:
            if isinstance(self.__classe, dict):
                with open(directory + "/" + filename, 'w') as outfile:
                    json.dump(json.loads(SmartJson._DictConversion(self.__classe).serialize(pretty=True)), outfile,
                              indent=2, sort_keys=True)
            elif isinstance(self.__classe, object):
                self.___obj = SmartJson._DataTypeConversion(self.__classe).next()

                if filename != "smart.json":
                    with open(directory + "/" + filename, 'w') as outfile:
                        json.dump(json.loads(
                            json.dumps({'' + self.classname: self._serialize(self.___obj).__dict__}, indent=2,
                                       sort_keys=True)), outfile, indent=2, sort_keys=True)
                else:
                    with open(directory + "/" + self.classname + ".json", 'w') as outfile:
                        json.dump(json.loads(
                            json.dumps({'' + self.classname: self._serialize(self.___obj).__dict__}, indent=2,
                                       sort_keys=True)), outfile, indent=2, sort_keys=True)



        except TypeError as e:
            SmartJson._UnsupportedClass((type(self.___obj).__name__), e)

    def toObjectFromFile(self, jsonFile):
        """
        :param jsonFile:
        :param obj_name:
        :return:
        """
        with open(jsonFile) as outfile:
            dic = json.load(outfile)

            return SmartJson._KObject(dic)

    def toObject(self, _json):
        """
        :param _json:
        :param obj_name:
        :return:
        """
        dic = None
        if isinstance(_json, str):
            dic = json.loads(_json)
        elif isinstance(_json, dict):
            dic = _json

        return SmartJson._KObject(dic)

    def getClass(self):
        return self.__copy

    def _serialize(self, obj):
        for attr, value in vars(obj).items():
            if hasattr(value, "__class__"):
                if isinstance(value, (
                        int, float, bool, complex, list, tuple, str, OrderedDict, dict,
                        datetime.datetime, datetime.date, bytes, type(None))):
                    continue
                elif SmartJson._JsonConvert().get_class_name(value) == "builtins.dict":
                    continue
                else:
                    obj.__setattr__(attr, value.__dict__)
                    self._serialize(value)

        return obj

    class _DataTypeConversion:
        def __init__(self, cls):
            self.___cls = cls
            self._json_cvt = SmartJson._JsonConvert()

        def next(self):
            try:
                return self.__next(self.___cls)
            except TypeError as e:
                SmartJson._UnsupportedClass((type(self.___cls).__name__), e)

        def __next(self, cls):
            for attr, value in vars(cls).items():
                if hasattr(value, "__class__"):
                    if isinstance(value, (datetime.datetime, datetime.date, complex)):
                        cls.__setattr__(attr, self._json_cvt.json_convert(value))
                    elif isinstance(value, (int, float, bool, str)):
                        continue
                    elif isinstance(value, (list, tuple)):
                        cls.__setattr__(attr, list((self._json_cvt.json_convert(v) for v in value)))
                    elif self._json_cvt.get_class_name(value) == "collections.deque":
                        cls.__setattr__(attr, self._json_cvt.json_convert(OrderedDict(value)))
                    elif isinstance(value, type(None)):
                        cls.__setattr__(attr, "")
                    elif isinstance(value, bytes):
                        cls.__setattr__(attr, value.decode("utf-8"))
                    elif isinstance(value, dict):
                        obj = [SmartJson._DictConversion(value).convert()]
                        cls.__setattr__(attr, obj)
                    else:
                        self.__next(value)

            return cls

    class _UnsupportedClass(Exception):
        def __init__(self, message, errors):
            # Call the base class constructor with the parameters it needs
            super().__init__(message)

            # Now for your custom code...
            self.errors = errors

            print("Error : 228 , UnsupportedClass : %s " % (message), errors)

    class _KObject(object):
        def __init__(self, d):
            for a, b in d.items():
                if isinstance(b, (list, tuple)):
                    setattr(self, a, [self.__class__(x) if isinstance(x, dict) else x for x in b])
                elif isinstance(b, str):
                    try:
                        setattr(self, a, datetime.datetime.strptime(b, "%Y-%m-%d %H:%M:%S.%f"))
                    except ValueError:
                        setattr(self, a, b)

                else:
                    setattr(self, a, self.__class__(b) if isinstance(b, dict) else b)

    class _DictConversion:
        def __init__(self, dict):
            self.__dict = deepcopy(dict)
            self._json_cvt = SmartJson._JsonConvert()

        def serialize(self, pretty):
            if pretty:
                return json.dumps(self.convert(), indent=2, sort_keys=True)
            else:
                return json.dumps(self.convert())

        def convert(self):
            for attr in self.__dict:
                if isinstance(self.__dict[attr], (datetime.date, datetime.datetime)):
                    self.__dict[attr] = str(self.__dict[attr])
                elif isinstance(self.__dict[attr], bytes):
                    self.__dict[attr] = self.__dict[attr].decode("utf-8")
                elif isinstance(self.__dict[attr], (list, tuple, set)):
                    self.__dict[attr] = [self._json_cvt.json_convert(item) for item in self.__dict[attr]]
                elif isinstance(self.__dict[attr], OrderedDict):
                    self.__dict[attr] = self._json_cvt.json_convert(self.__dict[attr])
                elif isinstance(self.__dict[attr], complex):
                    self.__dict[attr] = self._json_cvt.json_convert(self.__dict[attr])
                elif self._json_cvt.get_class_name(self.__dict[attr]) == "collections.deque":
                    self.__dict[attr] = self._json_cvt.json_convert(OrderedDict(self.__dict[attr]))
                elif hasattr(self.__dict[attr], "__class__"):
                    if isinstance(self.__dict[attr], (int, float, bool, str, type(None))):
                        continue
                    elif isinstance(self.__dict[attr], (list, tuple, set)):
                        self.__dict[attr] = {[self._json_cvt.json_convert(item) for item in self.__dict[attr]]}
                    else:
                        cls = self.__dict[attr]
                        serialize = SmartJson._DataTypeConversion(cls).next().__dict__
                        self.__dict[attr] = serialize

            return self.__dict
            # return json.dumps(self.__dict, indent=2, sort_keys=True)

    class _JsonConvert:

        self_dumpers = dict()
        self_loaders = dict()

        def self_dump(self, obj):
            class_name = self.get_class_name(obj)
            if class_name in self.self_dumpers:
                return self.self_dumpers[class_name](self, obj)
            raise TypeError("%r is not JSON serializable" % obj)

        def json_convert(self, obj):

            if isinstance(obj, OrderedDict):
                try:
                    return self.self_dump(obj)
                except TypeError:
                    return {k: self.json_convert(v) for k, v in self.iter_items(obj)}

            # nested dict
            elif isinstance(obj, dict):
                return {k: self.json_convert(v) for k, v in self.iter_items(obj)}

            # list or tuple
            elif isinstance(obj, (list, tuple)):
                return list((self.json_convert(v) for v in obj))

            elif isinstance(obj, (datetime.datetime, datetime.date)):
                return str(obj)

            elif isinstance(obj, complex):
                return [{'expression': str(obj), 'real': obj.real, 'imag': obj.imag}]

            elif hasattr(obj, "__class__"):
                if isinstance(obj, (int, float, bool, str, type(None))):
                    pass
                elif isinstance(obj, complex):
                    return [{'expression': str(obj), 'real': obj.real, 'imag': obj.imag}]
                else:
                    return SmartJson._DataTypeConversion(obj).next().__dict__

            # single object
            try:
                return self.self_dump(obj)
            except TypeError:
                return obj

        def iter_items(self, d, **kw):
            return iter(d.items(**kw))

        def get_class_name(self, obj):
            return obj.__class__.__module__ + "." + obj.__class__.__name__
