"""
Author : J. Koffi ONIPOH
Version : 1.0.0
email: jolli644@gmail.com
"""

import datetime
import json


class SuperJSON:
    def __init__(self, cls):
        """
        :param cls:
        """
        self.__classe = cls
        self.___obj = SuperJSON.__DataTypeConversion(cls).next()

    def serialize(self, pretty=True):
        """
        :param pretty:
        :return:
        """
        try:
            if pretty:
                return json.dumps(self.__serialize(self.___obj).__dict__, indent=2, sort_keys=True)
            else:
                return json.dumps(self.__serialize(self.___obj).__dict__, sort_keys=True)
        except TypeError as e:
            SuperJSON._UnsupportedClass((type(self.___obj).__name__), e)

    def toObjectFromFile(self, jsonFile):
        """
        :param jsonFile:
        :param obj_name:
        :return:
        """
        with open(jsonFile) as outfile:
            dic = json.load(outfile)

            return SuperJSON._KObject(dic)

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

        return SuperJSON._KObject(dic)

    def getClass(self):
        return self.__classe

    def __serialize(self, obj):
        for attr, value in vars(obj).items():
            if hasattr(value, "__class__"):
                if isinstance(value, (int, float, bool, complex, list, tuple, str, type(None))):
                    continue
                else:
                    obj.__setattr__(attr, value.__dict__)
                    self.__serialize(value)

        return obj

    class __DataTypeConversion:
        def __init__(self, cls):
            self.___cls = cls

        def next(self):
            try:
                return self.__next(self.___cls)
            except TypeError as e:
                SuperJSON._UnsupportedClass((type(self.___cls).__name__), e)

        def __next(self, cls):
            for attr, value in vars(cls).items():
                if hasattr(value, "__class__"):
                    if isinstance(value, (datetime.datetime, datetime.date, complex)):
                        cls.__setattr__(attr, str(value))
                    elif isinstance(value, (int, float, bool, tuple, list, str)):
                        continue
                    elif isinstance(value, type(None)):
                        cls.__setattr__(attr, "")
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
