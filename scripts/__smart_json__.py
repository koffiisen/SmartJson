"""
Author : J. Koffi ONIPOH
Version : 2.0.2
email: jolli644@gmail.com
"""

import datetime
import json
import os
from collections import OrderedDict
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
        visited_set = set() # Initialize for this top-level serialization call
        try:
            if isinstance(self.__classe, dict):
                return SmartJson._DictConversion(self.__classe, visited_set).serialize(pretty)
            elif isinstance(self.__classe, list):
                return SmartJson._ListConversion(self.__classe, visited_set).serialize(pretty)
            elif isinstance(self.__classe, (int, float, bool, str, type(None))):
                # Primitive types do not participate in circular dependencies themselves
                if pretty:
                    return json.dumps(self.__classe, indent=2, sort_keys=True)
                else:
                    return json.dumps(self.__classe, sort_keys=True)
            elif isinstance(self.__classe, (tuple, complex, datetime.date, datetime.datetime, OrderedDict)):
                # _JsonConvert needs to be instantiated with visited_set
                if pretty:
                    return json.dumps(self._JsonConvert(visited_set).json_convert(self.__classe), indent=2, sort_keys=True)
                else:
                    return json.dumps(self._JsonConvert(visited_set).json_convert(self.__classe), sort_keys=True)
            elif isinstance(self.__classe, object):
                if SmartJson._JsonConvert(visited_set).get_class_name(self.__classe) == "enum.EnumMeta": # Pass visited_set to _JsonConvert instance
                    return SmartJson._EnumConversion(self.__classe, visited_set).serialize(pretty)
                else:
                    self.___obj = SmartJson._DataTypeConversion(self.__classe, visited_set).convert()
                    # _serialize is a helper, cycle detection is handled by _DataTypeConversion.convert()
                    if pretty:
                        return json.dumps({'' + self.classname: self._serialize(self.___obj).__dict__}, indent=2,
                                          sort_keys=True)
                    else:
                        return json.dumps({'' + self.classname: self._serialize(self.___obj).__dict__}, sort_keys=True)
        except SmartJsonError: # Re-raise our specific errors
            raise
        except Exception as e: # Catch other unexpected errors
            obj_type = type(self.__classe).__name__
            if self.___obj: # If error happened after initial object processing
                obj_type = type(self.___obj).__name__
            raise SmartJsonSerializationError(f"Failed to serialize object of type '{obj_type}'", original_exception=e)


    def serializeToJsonFile(self, directory="output", filename="smart.json"):
        """
        Serializes the object to a JSON file.
        :param directory: The directory to save the file.
        :param filename: The name of the file.
        :raises SmartJsonSerializationError: If serialization or file writing fails.
        """
        try:
            os.makedirs(directory, exist_ok=True) # Use exist_ok=True
        except OSError as e:
            # This might catch permission errors for example
            raise SmartJsonSerializationError(f"Could not create directory '{directory}'", original_exception=e)

        try:
            serialized_data = self.serialize(pretty=True) # pretty=True for file output
            # Determine the correct filename if default is used
            output_filename = filename
            if filename == "smart.json" and hasattr(self, 'classname') and self.classname:
                 output_filename = self.classname + ".json"

            filepath = os.path.join(directory, output_filename)

            with open(filepath, 'w') as outfile:
                # self.serialize already returns a JSON string, no need to json.loads then json.dump
                outfile.write(serialized_data)

        except SmartJsonError: # Re-raise our specific errors from self.serialize()
            raise
        except Exception as e: # Catch other errors like file I/O issues
            obj_type = type(self.__classe).__name__
            raise SmartJsonSerializationError(f"Failed to serialize object of type '{obj_type}' to file '{filepath}'", original_exception=e)


    def toObjectFromFile(self, jsonFile):
        """
        Deserializes a JSON file to a Python object.

        :param jsonFile: Path to the JSON file.
        :return: A Python object (typically a _KObject instance).
        :raises SmartJsonDeserializationError: If the file is not found, not a valid JSON, or other deserialization issues.
        """
        try:
            with open(jsonFile) as outfile:
                dic = json.load(outfile)
                return SmartJson._KObject(dic)
        except FileNotFoundError:
            raise SmartJsonDeserializationError(f"JSON file not found: {jsonFile}")
        except json.JSONDecodeError as e:
            raise SmartJsonDeserializationError(f"Invalid JSON format in file '{jsonFile}': {e.message}", original_exception=e)
        except SmartJsonError: # Re-raise if _KObject init raises one
            raise
        except Exception as e: # Catch other potential errors
            raise SmartJsonDeserializationError(f"Error deserializing from file '{jsonFile}'", original_exception=e)


    def toObject(self, _json):
        """
        Deserializes a JSON string or dictionary to a Python object.

        :param _json: A JSON string or a Python dictionary.
        :return: A Python object (typically a _KObject instance).
        :raises SmartJsonDeserializationError: If input is invalid, JSON is malformed, or other deserialization issues.
        """
        dic = None
        try:
            if isinstance(_json, str):
                dic = json.loads(_json)
            elif isinstance(_json, dict):
                dic = _json
            else:
                raise SmartJsonDeserializationError(
                    f"Invalid input type for deserialization: Expected a JSON string or a dictionary, got {type(_json).__name__}.")

            return SmartJson._KObject(dic)
        except json.JSONDecodeError as e:
            raise SmartJsonDeserializationError(f"Invalid JSON format in input string: {e.message}", original_exception=e)
        except SmartJsonError: # Re-raise if _KObject init raises one
            raise
        except Exception as e: # Catch other errors during _KObject creation
            raise SmartJsonDeserializationError("Error converting input to object", original_exception=e)


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

    class _BaseConversion:
        """
        Base class for handling data type conversions to JSON-serializable formats.
        It provides common utilities like JSON serialization and a helper method
        for converting individual values.
        """
        def __init__(self, visited): # Accept visited set
            self.visited = visited # Store visited set
            self._json_cvt = SmartJson._JsonConvert(self.visited) # Pass visited to _JsonConvert

        def serialize(self, pretty):
            """
            Serializes the converted object to a JSON string.
            Uses the self.visited set managed by the instance.
            :param pretty: If True, the JSON will be pretty-printed.
            :return: A JSON string representing the converted object.
            """
            # self.convert() will use self.visited
            if pretty:
                return json.dumps(self.convert(), indent=2, sort_keys=True)
            else:
                return json.dumps(self.convert())

        def convert(self): # Uses self.visited implicitly
            """
            Main conversion method to be implemented by subclasses.
            This method should process the input data and return a
            JSON-serializable representation, using self.visited for cycle detection.
            """
            raise NotImplementedError("Subclasses must implement the convert() method.")

        def _convert_value(self, value): # Uses self.visited implicitly
            """
            Converts a single Python value into its JSON-serializable equivalent.

            Handles various standard types:
            - datetime.datetime, datetime.date, complex: Uses methods from _JsonConvert (which uses self.visited).
            - int, float, bool, str: Returned as is (not involved in cycles).
            - list, tuple: Recursively converts items, handles cycles.
            - collections.deque: Converted to an OrderedDict then processed by _JsonConvert.
            - enum.EnumMeta: Converted using _EnumConversion (passes self.visited).
            - None: Converted to an empty string.
            - bytes: Decoded to a UTF-8 string.
            - dict: Recursively converted using _DictConversion (passes self.visited), handles cycles.

            For custom objects (not matching any of the above types but having __class__),
            it converts them using _DataTypeConversion (which handles its own cycle)
            and then returns their __dict__ representation.

            :param value: The Python value to convert.
            :return: A JSON-serializable representation of the value.
            :raises SmartJsonCircularDependencyError: If a circular dependency is detected.
            """
            # Primitive types that don't cause cycles or are immutable don't need ID tracking here.
            if isinstance(value, (int, float, bool, str, type(None), bytes, datetime.date, datetime.datetime, complex)):
                # For bytes, datetime, complex, conversion might happen via _json_cvt if complex enough,
                # but the value itself isn't added to visited here as it's not a container for this method's check.
                if isinstance(value, bytes): return value.decode("utf-8")
                if isinstance(value, type(None)): return ""
                if isinstance(value, (datetime.datetime, datetime.date, complex)):
                    return self._json_cvt.json_convert(value) # _json_cvt handles its own visited logic for these
                return value

            # For container types (list, tuple, dict) and custom objects, check for cycles.
            obj_id = id(value)
            if obj_id in self.visited:
                raise SmartJsonCircularDependencyError(
                    f"Circular dependency detected in _convert_value for object type '{type(value).__name__}' (id: {obj_id})",
                    object_id=obj_id
                )

            self.visited.add(obj_id)
            try:
                if isinstance(value, (list, tuple)):
                    # Recursively convert items in lists/tuples
                    # Each item conversion will use the updated self.visited set.
                    return list((self._convert_value(v) for v in value))
                elif self._json_cvt.get_class_name(value) == "collections.deque":
                    # _json_cvt.json_convert will use the visited set from _json_cvt instance
                    return self._json_cvt.json_convert(OrderedDict(value))
                elif self._json_cvt.get_class_name(value) == "enum.EnumMeta":
                    # _EnumConversion constructor takes visited set
                    return SmartJson._EnumConversion(value, self.visited).convert()
                elif isinstance(value, dict):
                    # _DictConversion constructor takes visited set
                    return SmartJson._DictConversion(value, self.visited).convert()
                # Check for custom objects:
                elif not isinstance(value, (str, int, float, bool, type(None), # Already handled
                                            datetime.date, datetime.datetime, complex, bytes, # Already handled
                                            list, tuple)) and \
                     self._json_cvt.get_class_name(value) not in ["collections.deque", "enum.EnumMeta"] and \
                     hasattr(value, "__class__"):
                    # _DataTypeConversion constructor takes visited set. It handles its own add/remove for obj_id.
                    # So, we don't add/remove obj_id for it here again.
                    # The ID was added above, _DataTypeConversion will check it. If it proceeds,
                    # it will manage this ID for its own scope. This is a slight duplication of add/remove
                    # if _DataTypeConversion is called, as it will also add/remove.
                    # More accurately, _DataTypeConversion itself should handle the add/remove for the specific 'value'
                    # it processes, which is what it does now.
                    # So, the add/remove here is for the *current* value being processed by _convert_value.
                    # If 'value' is a custom object, _DataTypeConversion(value, self.visited) will be called.
                    # _DataTypeConversion.convert() will then do its own add(id(value))/remove(id(value)).
                    return SmartJson._DataTypeConversion(value, self.visited).convert().__dict__

                # Fallback for any other types not explicitly handled.
                # If it's a custom type not caught by the above, it might not be serializable.
                # The original code returned 'value', relying on json.dumps to fail.
                # We can do the same, or be stricter. For now, maintain original behavior.
                return value
            finally:
                if obj_id in self.visited: # Ensure it was added before removing
                    self.visited.remove(obj_id)

    class _DataTypeConversion(_BaseConversion):
        """
        Handles the conversion of attributes within a given class instance.
        It iterates over the instance's attributes and converts them to
        JSON-serializable types using the _convert_value method.
        The conversion happens in-place on the object's attributes.
        """
        def __init__(self, cls, visited): # Accept visited
            super().__init__(visited) # Pass visited to base
            self.___cls = cls  # The class instance to process

        def convert(self): # Uses self.visited from base class
            """
            Processes the attributes of the stored class instance.
            It iterates through the instance's __dict__, converting each attribute's
            value using _convert_value (which uses self.visited).
            The original instance is modified and then returned.

            :return: The modified class instance with its attributes converted.
            :raises SmartJsonCircularDependencyError: If a circular dependency is detected with this object.
            :raises SmartJsonUnsupportedTypeError: If an attribute type is not supported during conversion.
            :raises SmartJsonSerializationError: For other general serialization issues.
            """
            obj_id = id(self.___cls)
            if obj_id in self.visited:
                raise SmartJsonCircularDependencyError(
                    f"Circular dependency detected for object of type '{type(self.___cls).__name__}' (id: {obj_id})",
                    object_id=obj_id
                )

            self.visited.add(obj_id)
            try:
                return self.__convert_attributes(self.___cls)
            except SmartJsonError: # Re-raise specific SmartJson errors
                raise
            except Exception as e: # Catch other general errors, assume serialization context
                raise SmartJsonSerializationError(f"Error converting attributes for '{type(self.___cls).__name__}'", original_exception=e)
            finally:
                if obj_id in self.visited: # Ensure it was added before trying to remove
                    self.visited.remove(obj_id)

        def __convert_attributes(self, cls_obj): # self.visited is used by self._convert_value implicitly
            """Helper method to perform the attribute conversion."""
            for attr, value in vars(cls_obj).items():
                # Optimization: skip basic immutable types that don't need conversion
                if isinstance(value, (int, float, bool, str)):
                    continue

                # _convert_value will use self.visited for its cycle checks during deeper recursion
                converted_value = self._convert_value(value)
                cls_obj.__setattr__(attr, converted_value)
            return cls_obj

# --- Custom Exception Classes ---
class SmartJsonError(Exception):
    """Base class for exceptions in the SmartJson library."""
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception
        self.message = message # Store message separately for custom __str__

    def __str__(self):
        if self.original_exception:
            # Provide more context from the original exception if available
            return f"{self.message} (Caused by: {type(self.original_exception).__name__} - {str(self.original_exception)})"
        return self.message

class SmartJsonSerializationError(SmartJsonError):
    """Exception raised for errors specifically during the serialization process."""
    pass

class SmartJsonCircularDependencyError(SmartJsonSerializationError):
    """Exception raised when a circular dependency is detected during serialization."""
    def __init__(self, message="Circular dependency detected during serialization", object_id=None, original_exception=None):
        super().__init__(message, original_exception)
        self.object_id = object_id
        # Future enhancement: could include a path representation if complex debugging is needed.

class SmartJsonDeserializationError(SmartJsonError):
    """Exception raised for errors specifically during the deserialization process."""
    pass

class SmartJsonUnsupportedTypeError(SmartJsonError):
    """Exception raised when an unsupported data type is encountered during conversion."""
    pass
# --- End of Custom Exception Classes ---


    class _KObject(object):
        def __init__(self, d):
            if not isinstance(d, dict):
                raise SmartJsonDeserializationError(f"Cannot create _KObject from type '{type(d).__name__}'. Expected a dictionary structure.")
            for a, b in d.items():
                try:
                    if isinstance(b, (list, tuple)):
                        setattr(self, a, [self.__class__(x) if isinstance(x, dict) else x for x in b])
                    elif isinstance(b, str):
                        try:
                            setattr(self, a, datetime.datetime.strptime(b, "%Y-%m-%d %H:%M:%S.%f"))
                        except ValueError: # If not a datetime string, keep as string
                            setattr(self, a, b)
                    else:
                        setattr(self, a, self.__class__(b) if isinstance(b, dict) else b)
                except Exception as e:
                    # Catch errors during attribute setting, potentially from recursive _KObject creation
                    raise SmartJsonDeserializationError(f"Error processing attribute '{a}' for _KObject", original_exception=e)


    class _EnumConversion:
        def __init__(self, myEnum, visited): # Accept visited
            self.__myEnum = deepcopy(myEnum)
            self.visited = visited # Store visited set
            self._json_cvt = SmartJson._JsonConvert(self.visited) # Pass visited to _JsonConvert

        def serialize(self, pretty): # Uses self.visited implicitly via self.convert()
            if pretty:
                return json.dumps(self.convert(), indent=2, sort_keys=True)
            else:
                return json.dumps(self.convert())

        def convert(self): # Uses self.visited implicitly via calls to other converters
            """
            Converts an enum to a dictionary representation.
            :raises SmartJsonUnsupportedTypeError: If the object is not a supported enum type.
            """
            if self._json_cvt.get_class_name(self.__myEnum) == "enum.EnumMeta":
                converts = {}
                for attr, value in vars(self.__myEnum).items():
                    if "_member_names_" == attr:
                        for member_name in value: # Iterate through member names
                            # Access enum member by name to get its value
                            enum_member_value = self.__myEnum[member_name].value
                            converts[member_name] = enum_member_value
                # Pass self.visited to _DictConversion when converting enum's dict representation
                return SmartJson._DictConversion(converts, self.visited).convert()
            else:
                raise SmartJsonUnsupportedTypeError(f"Type '{type(self.__myEnum).__name__}' is not a directly serializable enum. Expected 'enum.EnumMeta'.")

    class _ListConversion(_BaseConversion):
        """
        Handles the conversion of items within a list to JSON-serializable formats.
        It iterates through the list, converting each item using _convert_value.
        Special handling is included to wrap converted dictionaries and enums
        in a single-item list to maintain original output structure.
        """
        def __init__(self, myList, visited): # Accept visited
            super().__init__(visited) # Pass visited to base
            self.__myList = deepcopy(myList) # Work on a copy

        # serialize method is inherited from _BaseConversion

        def convert(self): # Uses self.visited from base class
            """
            Converts each item in the internal list to its JSON-serializable equivalent.

            It uses the `_convert_value` method for individual item conversion.
            To maintain compatibility with the original behavior of SmartJson,
            items that were originally dictionaries or enums are wrapped in a
            single-item list after conversion if they are not already lists.

            :return: A new list with all items converted.
            """
            convert_result = []
            for item in self.__myList:
                converted_item = self._convert_value(item)

                # Preserve original behavior: wrap converted dicts and enums in a list
                # if they aren't already lists (e.g. from a list comprehension in _convert_value).
                # This applies if the *original* item was a dict or enum.
                if isinstance(item, dict) and not isinstance(converted_item, list):
                    # Original code: obj = [SmartJson._DictConversion(attr).convert()]
                    # _convert_value(item) for a dict returns the converted dict directly.
                    convert_result.append([converted_item])
                elif self._json_cvt.get_class_name(item) == "enum.EnumMeta" and not isinstance(converted_item, list):
                    # Original code: convert_result.append([SmartJson._EnumConversion(attr).convert()])
                    # _convert_value(item) for an enum returns the converted dict from _EnumConversion.
                    convert_result.append([converted_item])
                else:
                    convert_result.append(converted_item)
            return convert_result

    class _DictConversion(_BaseConversion):
        """
        Handles the conversion of values within a dictionary to JSON-serializable formats.
        It iterates through the dictionary's values, converting each using _convert_value.
        Special handling for enum values wraps them in a list to maintain original output.
        """
        def __init__(self, dictionary, visited): # Accept visited
            super().__init__(visited) # Pass visited to base
            # Use self.__data to avoid conflict with vars() or object's __dict__
            self.__data = deepcopy(dictionary) # Work on a copy

        # serialize method is inherited from _BaseConversion

        def convert(self): # Uses self.visited from base class
            """
            Converts each value in the internal dictionary to its JSON-serializable equivalent.

            It uses the `_convert_value` method for individual value conversion.
            To maintain compatibility with the original behavior, if a value was
            originally an enum, its converted form (a dictionary) is wrapped
            in a single-item list if it's not already a list.
            The conversion modifies the dictionary in place.

            :return: The modified dictionary with its values converted.
            """
            for key, value in self.__data.items(): # Iterate over original key-value pairs
                converted_value = self._convert_value(value)
                self.__data[key] = converted_value

                # Preserve original behavior: wrap converted enums in a list.
                # This applies if the *original* value was an enum.
                if self._json_cvt.get_class_name(value) == "enum.EnumMeta" and \
                   not isinstance(self.__data[key], list): # Check current (converted) value type
                     self.__data[key] = [self.__data[key]] # Wrap if it's not already a list

            return self.__data

    class _JsonConvert:
        def __init__(self, visited=None):
            self.visited = visited if visited is not None else set()
            # self_dumpers and self_loaders are class variables.

        self_dumpers = dict() # Class variable
        self_loaders = dict() # Class variable

        def self_dump(self, obj): # Visited is implicitly self.visited
            class_name = self.get_class_name(obj)
            if class_name in self.self_dumpers:
                try:
                    return self.self_dumpers[class_name](self, obj)
                except Exception as e:
                    raise SmartJsonSerializationError(f"Custom dumper for '{class_name}' failed", original_exception=e)
            # This error indicates no custom dumper was found for a type that might have expected one.
            raise SmartJsonUnsupportedTypeError(f"Object of type '{class_name}' is not JSON serializable with a custom dumper and no default path available in self_dump.")

        def json_convert(self, obj): # Visited is implicitly self.visited due to __init__
            """
            Main internal conversion routing method.
            Attempts to convert various Python objects to JSON-serializable forms.
            Uses self.visited for cycle detection in recursive calls.
            """
            # Handle types that don't participate in cycles or are immutable first.
            if isinstance(obj, (int, float, bool, str, type(None), bytes, datetime.date, datetime.datetime, complex)):
                if isinstance(obj, bytes): return obj.decode("utf-8")
                if isinstance(obj, type(None)): return ""
                if isinstance(obj, (datetime.datetime, datetime.date)): return str(obj)
                if isinstance(obj, complex): return [{'expression': str(obj), 'real': obj.real, 'imag': obj.imag}]
                return obj

            # For container types and custom objects, check for cycles.
            obj_id = id(obj)
            if obj_id in self.visited:
                raise SmartJsonCircularDependencyError(
                    f"Circular dependency detected in json_convert for object type '{type(obj).__name__}' (id: {obj_id})",
                    object_id=obj_id
                )
            self.visited.add(obj_id)

            try:
                if isinstance(obj, OrderedDict):
                    try:
                        return self.self_dump(obj) # self_dump uses self.visited implicitly
                    except SmartJsonUnsupportedTypeError:
                        return {k: self.json_convert(v) for k, v in self.iter_items(obj)} # Recursive call
                elif isinstance(obj, dict):
                    return {k: self.json_convert(v) for k, v in self.iter_items(obj)} # Recursive call
                elif isinstance(obj, (list, tuple)):
                    return list((self.json_convert(v) for v in obj)) # Recursive call

                # General custom object not covered by specific type checks above (e.g., not OrderedDict)
                # This is a fallback path. _BaseConversion._convert_value is usually more direct.
                elif hasattr(obj, "__class__"):
                    # _DataTypeConversion handles its own add/remove from visited set for 'obj'
                    return SmartJson._DataTypeConversion(obj, self.visited).convert().__dict__

                # Fallback for types that might have a custom dumper but weren't caught by earlier checks.
                # This path is less likely if _BaseConversion._convert_value is comprehensive.
                try:
                    return self.self_dump(obj) # self_dump uses self.visited implicitly
                except SmartJsonUnsupportedTypeError:
                     # If no custom dumper, and not a known type, this object might not be serializable.
                     # Return obj and let json.dumps handle the final TypeError.
                    return obj
            finally:
                if obj_id in self.visited: # Ensure it was added before trying to remove
                    self.visited.remove(obj_id)
        # Outer try-except for SmartJsonError/Exception removed as it was too broad for this method.
        # Errors should propagate to be caught by the primary serialization methods.

        def iter_items(self, d, **kw):
            return iter(d.items(**kw))

        def get_class_name(self, obj):
            return obj.__class__.__module__ + "." + obj.__class__.__name__
