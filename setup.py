from setuptools import setup, find_packages
import io # To ensure consistent encoding for README

# Read the contents of your README file
# This will be used as the long description
with io.open("README.md", "r", encoding="utf-8") as fh: # Added encoding="utf-8"
    long_description = fh.read()

setup(
    name='smartjson',
    version='2.1.0', # Updated version
    author="J. Koffi ONIPOH",
    author_email="jolli644@gmail.com",
    description="A Python library for seamless serialization of Python objects/dictionaries to JSON and deserialization of JSON back to Python objects, with schema validation capabilities.", # Updated description
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/koffiisen/SmartJson", # Existing URL
    project_urls={ # New project URLs
        'Documentation': 'https://github.com/koffiisen/SmartJson#readme',
        'Source': 'https://github.com/koffiisen/SmartJson',
        'Tracker': 'https://github.com/koffiisen/SmartJson/issues',
        'Changelog': 'https://github.com/koffiisen/SmartJson/blob/main/CHANGELOG.md', # Assuming main branch
    },
    keywords=[ # Updated keywords
        'json', 'serialize', 'deserialize', 'serialization', 'deserialization',
        'json conversion', 'python to json', 'json to python', 'schema validation',
        'object mapper', 'datetime', 'enum', 'complex', 'OrderedDict', 'deque'
    ],
    packages=find_packages(exclude=("tests*", "examples*")), # Exclude tests and examples
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
    install_requires=[
        'six>=1.10.0',
        'enum34; python_version<"3.4"',
    ],
    include_package_data=True, # Changed to True
    # package_data={ # Example if you had non-code files inside your package
    #     'smartjson': ['some_data_file.dat'],
    # },
    classifiers=[ # Updated classifiers
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
