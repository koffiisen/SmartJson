# examples/04_file_operations.py
from __future__ import print_function, unicode_literals, division, absolute_import
from smartjson import SmartJson
from smartjson.__smart_json__ import SmartJsonSchemaValidationError # For catching the specific error
import datetime
import os
import six # For types in schema
import io # For file writing in example

print("### File Operations Demo (serializeToJsonFile and toObjectFromFile) ###")

# --- Define a simple class ---
class Article:
    def __init__(self, title, author, publication_date, content_summary=None):
        self.title = title
        self.author = author
        self.publication_date = publication_date # datetime.date object
        if content_summary:
            self.content_summary = content_summary

# --- Schema for Serialization (using Python types) ---
article_schema_serialization = {
    'title': {'type': six.string_types, 'required': True},
    'author': {'type': six.string_types, 'required': True},
    'publication_date': {'type': datetime.date, 'required': True},
    'content_summary': {'type': six.string_types, 'required': False}
}

# --- Schema for Deserialization (using string type names) ---
# Note: datetime.date becomes "str" after JSON serialization.
article_schema_deserialization = {
    'title': {'type': "str", 'required': True},
    'author': {'type': "str", 'required': True},
    'publication_date': {'type': "str", 'required': True}, # Dates are strings in JSON
    'content_summary': {'type': "str", 'required': False}
}


# --- Create an Article instance ---
article_obj = Article(
    title="The Future of AI",
    author="Dr. AI Expert",
    publication_date=datetime.date(2024, 3, 10),
    content_summary="An insightful look into upcoming AI trends."
)

# --- Serialize to JSON File (with and without schema) ---
print("\n--- Serializing to JSON File ---")
sj_article = SmartJson(article_obj)
output_dir = "output_examples" # Create a subdirectory for output

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

file_no_schema_path = os.path.join(output_dir, "article_no_schema.json")
file_with_schema_path = os.path.join(output_dir, "article_with_schema.json")

print("Serializing article to '{}' (no schema)...".format(file_no_schema_path))
sj_article.serializeToJsonFile(directory=output_dir, filename="article_no_schema.json")
print("Serialization without schema complete.")

print("\nSerializing article to '{}' (with schema)...".format(file_with_schema_path))
try:
    sj_article.serializeToJsonFile(directory=output_dir, filename="article_with_schema.json", schema=article_schema_serialization)
    print("Serialization with schema complete.")
except SmartJsonSchemaValidationError as e:
    print("Error during serialization with schema:", e)


# --- Deserialize from JSON File (with and without schema) ---
print("\n\n--- Deserializing from JSON File ---")
sj_deserializer = SmartJson()

# Deserialize without schema
print("Deserializing from '{}' (no schema)...".format(file_no_schema_path))
try:
    article_from_file_no_schema = sj_deserializer.toObjectFromFile(file_no_schema_path)
    # Accessing data: SmartJson wraps the object content under its class name key if original was object
    data = getattr(article_from_file_no_schema, article_obj.__class__.__name__, article_from_file_no_schema)
    print("Title (no schema): {}".format(data.title))
except Exception as e:
    print("Error deserializing '{}': {}".format(file_no_schema_path, e))


# Deserialize with schema
print("\nDeserializing from '{}' (with schema)...".format(file_with_schema_path))
try:
    article_from_file_with_schema = sj_deserializer.toObjectFromFile(file_with_schema_path, schema=article_schema_deserialization)
    data_ws = getattr(article_from_file_with_schema, article_obj.__class__.__name__, article_from_file_with_schema)
    print("Title (with schema): {}".format(data_ws.title))
    print("Author (with schema): {}".format(data_ws.author))
    # Note: publication_date will be a string here as per JSON format and deserialization schema
    print("Publication Date (with schema, as string): {}".format(data_ws.publication_date))
except SmartJsonSchemaValidationError as e:
    print("Schema validation error deserializing '{}': {}".format(file_with_schema_path, e))
except Exception as e:
    print("Error deserializing '{}': {}".format(file_with_schema_path, e))

# Example of trying to deserialize a file that would fail schema validation
malformed_article_content = '''
{
    "title": "Incomplete Article",
    "publication_date": "2024-03-11"
}
''' # Missing required 'author'
malformed_file_path = os.path.join(output_dir, "malformed_article.json")
# Use io.open for writing this example file to ensure unicode handling
with io.open(malformed_file_path, "w", encoding='utf-8') as f:
    f.write(malformed_article_content if six.PY3 else malformed_article_content.decode('utf-8'))


print("\nDeserializing from malformed file '{}' (with schema)...".format(malformed_file_path))
try:
    sj_deserializer.toObjectFromFile(malformed_file_path, schema=article_schema_deserialization)
except SmartJsonSchemaValidationError as e:
    print("Caught expected schema validation error for malformed file: {}".format(e))
except Exception as e:
    print("Error deserializing malformed file: {}".format(e))

print("\n\nNote: Example JSON files are saved in the '{}' directory.".format(output_dir))
