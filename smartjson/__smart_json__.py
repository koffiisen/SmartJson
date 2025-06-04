from __future__ import print_function, unicode_literals, division, absolute_import
import six # For Python 2/3 compatibility
import io  # For consistent file I/O
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

    def serialize(self, pretty=True, schema=None):
        """
        Serializes the current object (or dictionary/list) to a JSON string.

        Optionally validates the object against a schema before serialization.

        :param pretty: If True, the output JSON string will be pretty-printed (indented).
                       Defaults to True.
        :param schema: Optional. A dictionary defining the schema to validate the object against
                       before serialization. If validation fails, SmartJsonSchemaValidationError is raised.
                       See documentation for schema definition structure.
        :return: A JSON string representing the object.
        :raises SmartJsonCircularDependencyError: If a circular dependency is detected during serialization.
        :raises SmartJsonSerializationError: For general errors during serialization.
        :raises SmartJsonSchemaValidationError: If schema validation is enabled and fails.
        :raises SmartJsonUnsupportedTypeError: If an unsupported type is encountered that cannot be serialized.
        """
        if schema:
            # self.__classe is the original object/dict passed to SmartJson
            SmartJson._validate_object(self.__classe, schema)

        visited_set = set() # Initialize for this top-level serialization call
        try:
            if isinstance(self.__classe, dict):
                return SmartJson._DictConversion(self.__classe, visited_set).serialize(pretty)
            elif isinstance(self.__classe, list):
                return SmartJson._ListConversion(self.__classe, visited_set).serialize(pretty)
            # Adjusted str check for six.string_types
            elif isinstance(self.__classe, (int, float, bool, six.string_types, type(None))):
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


    def serializeToJsonFile(self, directory="output", filename="smart.json", schema=None):
        """
        Serializes the current object (or dictionary/list) to a JSON file.

        Optionally validates the object against a schema before serialization.

        :param directory: The directory where the JSON file will be saved. Defaults to "output".
        :param filename: The name of the JSON file. Defaults to "smart.json" for basic types
                         or "[classname].json" for objects if `classname` is available.
        :param schema: Optional. A dictionary defining the schema to validate the object against
                       before serialization. If validation fails, SmartJsonSchemaValidationError is raised.
                       See documentation for schema definition structure.
        :raises SmartJsonSerializationError: For general errors during serialization or file writing.
        :raises SmartJsonSchemaValidationError: If schema validation is enabled and fails.
        :raises SmartJsonCircularDependencyError: If a circular dependency is detected.
        :raises SmartJsonUnsupportedTypeError: If an unsupported type is encountered.
        """
        if schema:
            # self.__classe is the original object/dict passed to SmartJson
            SmartJson._validate_object(self.__classe, schema)

        try:
            os.makedirs(directory, exist_ok=True) # Use exist_ok=True
        except OSError as e:
            # This might catch permission errors for example
            raise SmartJsonSerializationError(f"Could not create directory '{directory}'", original_exception=e)

        try:
            # Pass schema=None here because validation is already done at the beginning of this method.
            # Or, ensure self.serialize doesn't re-validate if called internally after a top-level validation.
            # For now, assuming self.serialize will handle schema=None if it's the primary entry.
            # However, serializeToJsonFile calls self.serialize(). If schema is passed to serializeToJsonFile,
            # it should ideally be passed down to self.serialize() if not handled at this top level.
            # The current implementation validates at the beginning of THIS method, then calls self.serialize().
            # The self.serialize() might re-validate if schema is passed again.
            # Let's pass schema=None to self.serialize here, as validation is done above.
            serialized_data = self.serialize(pretty=True, schema=None) # Validate once at this level

            # Determine the correct filename if default is used
            output_filename = filename
            if filename == "smart.json" and hasattr(self, 'classname') and self.classname:
                 output_filename = self.classname + ".json"

            filepath = os.path.join(directory, output_filename)

            # Use io.open for consistent encoding
            with io.open(filepath, 'w', encoding='utf-8') as outfile:
                if six.PY2 and isinstance(serialized_data, str): # str in Py2 is bytes
                    serialized_data = serialized_data.decode('utf-8')
                outfile.write(serialized_data)

        except SmartJsonError:
            raise
        except Exception as e:
            obj_type = type(self.__classe).__name__
            raise SmartJsonSerializationError(f"Failed to serialize object of type '{obj_type}' to file '{filepath}'", original_exception=e)


    def toObjectFromFile(self, jsonFile, schema=None):
        """
        Deserializes a JSON file to a Python object, with optional schema validation.

        The resulting object is a `_KObject` instance, allowing attribute-style access
        to the deserialized data.

        :param jsonFile: Path to the JSON file.
        :param schema: Optional. A dictionary defining the schema to validate the JSON data against
                       after parsing. If validation fails, SmartJsonSchemaValidationError is raised.
                       See documentation for schema definition structure.
        :return: A Python object (typically a `_KObject` instance).
        :raises SmartJsonDeserializationError: If the file is not found, is not valid JSON,
                                             or other issues occur during deserialization.
        :raises SmartJsonSchemaValidationError: If schema validation is enabled and fails.
        """
        try:
            # Use io.open for consistent encoding
            with io.open(jsonFile, 'r', encoding='utf-8') as outfile:
                dic = json.load(outfile)

            if schema:
                SmartJson._validate_data(dic, schema) # Call validation

            return SmartJson._KObject(dic)
        except FileNotFoundError: # Py3 specific, Py2 uses IOError
            raise SmartJsonDeserializationError(f"JSON file not found: {jsonFile}")
        except IOError as e: # Catch Py2's FileNotFoundError equivalent
            if e.errno == 2: # errno.ENOENT
                 raise SmartJsonDeserializationError(f"JSON file not found: {jsonFile}")
            raise SmartJsonDeserializationError(f"I/O error reading file '{jsonFile}'", original_exception=e)
        except json.JSONDecodeError as e:
            raise SmartJsonDeserializationError(f"Invalid JSON format in file '{jsonFile}': {e.message}", original_exception=e)
        except SmartJsonError: # Re-raise if _KObject init or _validate_data raises one
            raise
        except Exception as e: # Catch other potential errors
            raise SmartJsonDeserializationError(f"Error deserializing from file '{jsonFile}'", original_exception=e)

    @staticmethod
    def _validate_object(obj, schema, path=""):
        """
        Validates a Python object or dictionary against a schema before serialization.

        This method checks for required fields, correct Python types, and recursively validates
        nested objects/dictionaries and lists of objects/typed items based on the schema.

        The schema is expected to define fields with properties like 'type' (actual Python type),
        'required' (boolean), 'schema' (for nested objects/dicts), 'item_type' (for list items' type),
        and 'item_schema' (for schema of objects within a list).

        :param obj: The Python object or dictionary to validate.
        :param schema: A dictionary representing the schema.
        :param path: A string representing the current validation path for error messages
                     (e.g., "user.address" or "items[0]").
        :raises SmartJsonSchemaValidationError: If any validation check fails.
        """
        if not isinstance(schema, dict):
            raise SmartJsonSchemaValidationError(f"Invalid schema definition at '{path}': schema must be a dictionary.")

        is_obj_dict = isinstance(obj, dict)

        for field_name, field_props in six.iteritems(schema):
            current_path = f"{path}.{field_name}" if path else field_name

            if not isinstance(field_props, dict):
                raise SmartJsonSchemaValidationError(f"Invalid schema definition for field '{current_path}': properties must be a dictionary.")

            is_required = field_props.get('required', False)
            # In serialization, 'type' in schema refers to the expected Python type of the attribute/value.
            expected_py_type = field_props.get('type')

            attr_exists = hasattr(obj, field_name) if not is_obj_dict else field_name in obj

            if is_required and not attr_exists:
                obj_type_name = type(obj).__name__
                raise SmartJsonSchemaValidationError(f"Missing required attribute/key: '{current_path}' on object/dict of type '{obj_type_name}'.")

            if attr_exists:
                value = getattr(obj, field_name) if not is_obj_dict else obj[field_name]

                if expected_py_type:
                    # Direct type comparison for basic types, allow schema to specify classes for custom types
                    if not isinstance(value, expected_py_type):
                        raise SmartJsonSchemaValidationError(
                            f"Invalid type for attribute/key '{current_path}'. Expected {expected_py_type.__name__}, got {type(value).__name__}.")

                    # After type check, if a sub-schema is provided for this field, validate it.
                    # This applies if expected_py_type was 'dict' and has a 'schema',
                    # OR if expected_py_type was a custom class and has an associated 'schema' for its attributes.
                    if 'schema' in field_props:
                        # Ensure 'value' is an object or dict before applying a dict-like schema to it.
                        # The isinstance check above should have already verified 'value' against expected_py_type.
                        # If expected_py_type is not dict or a custom class, having a 'schema' entry might be a schema design error,
                        # but we proceed if value is suitable for attribute/key based validation.
                        if isinstance(value, (dict)) or hasattr(value, '__dict__'): # Suitable for recursive _validate_object
                             SmartJson._validate_object(value, field_props['schema'], path=current_path)
                        # else: value is of expected_py_type, but not dict-like, yet a sub-schema is provided.
                        # This could be an error or a specific use case (e.g. schema for a list's own properties, not items).
                        # For now, if not dict-like, we don't recurse with field_props['schema'].

                    elif expected_py_type == list and ('item_type' in field_props or 'item_schema' in field_props):
                        item_expected_py_type = field_props.get('item_type') # This should be a Python type/class
                        item_schema_def = field_props.get('item_schema')

                        if not isinstance(value, list): # Value of the field itself must be a list
                             raise SmartJsonSchemaValidationError(f"Attribute/key '{current_path}' expected to be a list, got {type(value).__name__}.")

                        for idx, item in enumerate(value):
                            item_path = f"{current_path}[{idx}]"

                            if item_expected_py_type: # Check type of item in list
                                if not isinstance(item, item_expected_py_type):
                                    raise SmartJsonSchemaValidationError(
                                        f"Invalid type for item at '{item_path}'. Expected {item_expected_py_type.__name__}, got {type(item).__name__}.")

                            if item_schema_def: # If items themselves have a schema (e.g. list of objects)
                                # If item_schema is present, 'item' should be suitable for _validate_object
                                # (i.e., an object or a dictionary).
                                if isinstance(item, (dict)) or hasattr(item, '__dict__'):
                                    SmartJson._validate_object(item, item_schema_def, path=item_path)
                                elif item_expected_py_type and not (isinstance(item, dict) or hasattr(item, '__dict__')):
                                    # This case means item_schema is provided, but item is not dict-like,
                                    # AND item_expected_py_type was something else (e.g. str). Schema conflict.
                                    raise SmartJsonSchemaValidationError(
                                        f"Schema for item at '{item_path}' provided, but item type '{type(item).__name__}' is not an object or dictionary.")

        # Note: Extra attributes/keys on the object/dict not in the schema are allowed by default.

    def toObject(self, _json, schema=None):
        """
        Deserializes a JSON string or dictionary to a Python object, with optional schema validation.

        The resulting object is a `_KObject` instance, allowing attribute-style access
        to the deserialized data.

        :param _json: A JSON string, bytes, or a Python dictionary.
        :param schema: Optional. A dictionary defining the schema to validate the JSON data against
                       after parsing (if input is string/bytes) or directly (if input is dict).
                       If validation fails, SmartJsonSchemaValidationError is raised.
                       See documentation for schema definition structure.
        :return: A Python object (typically a `_KObject` instance).
        :raises SmartJsonDeserializationError: If input is invalid, JSON is malformed,
                                             or other issues occur during deserialization.
        :raises SmartJsonSchemaValidationError: If schema validation is enabled and fails.
        """
        dic = None
        try:
            if isinstance(_json, six.binary_type): # Handle bytes input
                _json = _json.decode('utf-8')

            if isinstance(_json, six.string_types):
                dic = json.loads(_json)
            elif isinstance(_json, dict):
                dic = _json
            else:
                raise SmartJsonDeserializationError(
                    f"Invalid input type for deserialization: Expected a JSON string, bytes, or a dictionary, got {type(_json).__name__}.")

            if schema and dic is not None: # Ensure dic is populated before validation
                SmartJson._validate_data(dic, schema) # Call validation

            return SmartJson._KObject(dic)
        except json.JSONDecodeError as e:
            raise SmartJsonDeserializationError(f"Invalid JSON format in input: {e.message}", original_exception=e)
        except UnicodeDecodeError as e:
            raise SmartJsonDeserializationError("Input bytes could not be decoded using UTF-8", original_exception=e)
        except SmartJsonError: # Re-raise if _KObject init or _validate_data raises one
            raise
        except Exception as e: # Catch other errors during _KObject creation
            raise SmartJsonDeserializationError("Error converting input to object", original_exception=e)

    @staticmethod
    def _validate_data(data, schema, path=""):
        """
        Validates JSON-like data (Python dictionaries/lists post-JSON parsing) against a schema.

        This method is used during deserialization. It checks for required fields, correct data types
        (mapping JSON types to expected Python types via string names like "str", "int", "list", "dict"),
        and recursively validates nested dictionaries and lists of items.

        The schema is expected to define fields with properties like 'type' (string name of type),
        'required' (boolean), 'schema' (for nested dicts), 'item_type' (string name for list items' type),
        and 'item_schema' (for schema of dicts within a list).

        :param data: The Python dictionary or list (parsed from JSON) to validate.
        :param schema: A dictionary representing the schema.
        :param path: A string representing the current validation path for error messages
                     (e.g., "user.address" or "items[0]").
        :raises SmartJsonSchemaValidationError: If any validation check fails.
        """
        if not isinstance(schema, dict):
            # For now, we assume the top-level schema is always a dictionary defining an object.
            # This could be expanded later if schemas for lists or primitives at the top level are needed.
            raise SmartJsonSchemaValidationError(f"Invalid schema definition at '{path}': schema itself must be a dictionary.")

        if not isinstance(data, dict):
            raise SmartJsonSchemaValidationError(f"Invalid data type at '{path or "root"}'. Expected a dictionary, got {type(data).__name__}.")

        for field_name, field_props in six.iteritems(schema):
            current_path = f"{path}.{field_name}" if path else field_name

            if not isinstance(field_props, dict):
                raise SmartJsonSchemaValidationError(f"Invalid schema definition for field '{current_path}': properties must be a dictionary.")

            is_required = field_props.get('required', False)
            field_type_name = field_props.get('type') # Type name as string e.g. "str", "int", "list", "dict"

            # Python type mapping - can be expanded
            TYPE_MAP = {
                "str": six.string_types,
                "int": six.integer_types, # Catches int, long in Py2
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                # Custom class types could be registered here or handled differently
            }

            if is_required and field_name not in data:
                raise SmartJsonSchemaValidationError(f"Missing required field: '{current_path}'")

            if field_name in data:
                value = data[field_name]

                if field_type_name: # If type is specified in schema
                    expected_type = TYPE_MAP.get(field_type_name)
                    if not expected_type:
                        # This means the schema specified a type name we don't have in TYPE_MAP
                        # Could be a custom class name, or an unsupported basic type string
                        # For now, we'll raise an error for unmapped basic types.
                        # Custom class type validation would be more complex (e.g. value is dict, field_type_name is 'MyClass')
                        raise SmartJsonSchemaValidationError(f"Unknown type '{field_type_name}' specified in schema for field '{current_path}'.")

                    if not isinstance(value, expected_type):
                        actual_type_name = type(value).__name__
                        if isinstance(value, six.integer_types): actual_type_name = "int"
                        elif isinstance(value, six.string_types): actual_type_name = "str"
                        raise SmartJsonSchemaValidationError(
                            f"Invalid type for field '{current_path}'. Expected '{field_type_name}', got '{actual_type_name}'.")

                    # Handle nested schemas for dicts and lists
                    if field_type_name == "dict" and 'schema' in field_props:
                        # Recursive call for nested dictionary schema
                        SmartJson._validate_data(value, field_props['schema'], path=current_path)

                    elif field_type_name == "list" and ('item_type' in field_props or 'item_schema' in field_props):
                        item_type_name = field_props.get('item_type')
                        item_schema_def = field_props.get('item_schema')

                        for idx, item in enumerate(value):
                            item_path = f"{current_path}[{idx}]"

                            if item_type_name:
                                expected_item_type = TYPE_MAP.get(item_type_name)
                                if not expected_item_type:
                                    raise SmartJsonSchemaValidationError(
                                        f"Unknown item_type '{item_type_name}' in list schema for field '{current_path}'.")
                                if not isinstance(item, expected_item_type):
                                    actual_item_type_name = type(item).__name__
                                    if isinstance(item, six.integer_types): actual_item_type_name = "int"
                                    elif isinstance(item, six.string_types): actual_item_type_name = "str"
                                    raise SmartJsonSchemaValidationError(
                                        f"Invalid type for item at '{item_path}'. Expected '{item_type_name}', got '{actual_item_type_name}'.")

                            if item_schema_def:
                                if not isinstance(item, dict): # Item must be a dict if item_schema is provided
                                    raise SmartJsonSchemaValidationError(
                                        f"Invalid item type at '{item_path}'. Expected a dictionary for schema validation, got {type(item).__name__}.")
                                # Recursive call for nested schema within list items
                                SmartJson._validate_data(item, item_schema_def, path=item_path)

        # (Optional: Add check for extra fields in data not defined in schema here if desired)


    def getClass(self):
        return self.__copy

    def _serialize(self, obj):
        # This method's original recursive logic is now handled by _DataTypeConversion and _convert_value.
        # self.___obj (which is passed as 'obj' here) should already have its attributes
        # converted to JSON-serializable forms (e.g., custom objects replaced by their dicts)
        # by the time _DataTypeConversion(...).convert() finishes.
        # Therefore, this method primarily serves to return the object itself,
        # as its __dict__ will be taken by the caller in SmartJson.serialize().

        # A check could be added here to ensure obj's attributes are indeed serializable,
        # but the current design relies on earlier stages to have done this.
        # For Py2/3 with six, vars(obj).items() should be six.iteritems(vars(obj)) if we were iterating.
        # However, since this method is now a pass-through, no iteration is done here.
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
            # Use six.string_types for string check, six.binary_type for bytes.
            if isinstance(value, (int, float, bool, six.string_types, type(None), six.binary_type, datetime.date, datetime.datetime, complex)):
                if isinstance(value, six.binary_type): return value.decode("utf-8")
                if isinstance(value, type(None)): return "" # Keep original behavior
                if isinstance(value, (datetime.datetime, datetime.date, complex)):
                    return self._json_cvt.json_convert(value)
                # int, float, bool, six.string_types are returned as is
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
                # Adjusted string/bytes check for the custom object path using six
                elif not isinstance(value, (six.string_types, int, float, bool, type(None), # Already handled
                                            datetime.date, datetime.datetime, complex, six.binary_type, # Already handled
                                            list, tuple)) and \
                     self._json_cvt.get_class_name(value) not in ["collections.deque", "enum.EnumMeta"] and \
                     hasattr(value, "__class__"):
                    # _DataTypeConversion constructor takes visited set. It handles its own add/remove for obj_id.
                    return SmartJson._DataTypeConversion(value, self.visited).convert().__dict__

                return value # Fallback
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
            # Use six.iteritems for iterating over dictionary items
            for attr, value in six.iteritems(vars(cls_obj)):
                # Optimization: skip basic immutable types that don't need conversion
                # Use six.string_types for string check
                if isinstance(value, (int, float, bool, six.string_types)):
                    continue

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

class SmartJsonSchemaValidationError(SmartJsonError):
    """
    Exception raised when data fails schema validation during serialization or deserialization.

    Attributes:
        message (str): The error message, often including the path to the invalid field.
        original_exception (Exception, optional): The original exception, if any, that led to this error.
    """
    pass
# --- End of Custom Exception Classes ---


    class _KObject(object):
        def __init__(self, d):
            if not isinstance(d, dict):
                raise SmartJsonDeserializationError(f"Cannot create _KObject from type '{type(d).__name__}'. Expected a dictionary structure.")
            # Use six.iteritems for iterating dictionary items
            for a, b in six.iteritems(d):
                try:
                    if isinstance(b, (list, tuple)):
                        setattr(self, a, [self.__class__(x) if isinstance(x, dict) else x for x in b])
                    # Use six.string_types for string check
                    elif isinstance(b, six.string_types):
                        try:
                            # Attempt to parse as datetime
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
                # Use six.iteritems for iterating dictionary items
                for attr, value in six.iteritems(vars(self.__myEnum)):
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
            # Use six.iteritems for iterating dictionary items
            for key, value in six.iteritems(self.__data): # Iterate over original key-value pairs
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
            # Use six.string_types and six.binary_type
            if isinstance(obj, (int, float, bool, six.string_types, type(None), six.binary_type, datetime.date, datetime.datetime, complex)):
                if isinstance(obj, six.binary_type): return obj.decode("utf-8")
                if isinstance(obj, type(None)): return ""
                if isinstance(obj, (datetime.datetime, datetime.date)): return str(obj)
                if isinstance(obj, complex): return [{'expression': str(obj), 'real': obj.real, 'imag': obj.imag}]
                return obj # int, float, bool, six.string_types

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
                        # Use six.iteritems for iterating dictionary items
                        return {k: self.json_convert(v) for k, v in six.iteritems(obj)} # Recursive call
                elif isinstance(obj, dict):
                    # Use six.iteritems for iterating dictionary items
                    return {k: self.json_convert(v) for k, v in six.iteritems(obj)} # Recursive call
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

        def iter_items(self, d, **kw): # This method is used by json_convert for OrderedDicts.
            return six.iteritems(d, **kw) # Use six.iteritems

        def get_class_name(self, obj):
            return obj.__class__.__module__ + "." + obj.__class__.__name__
