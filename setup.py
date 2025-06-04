from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    setup(
        name='smartjson',
        version='2.0.3',
        author="J. Koffi ONIPOH",
        author_email="jolli644@gmail.com",
        description="Python libraries to convert class to json or Tool to convert Class, object and dict to Json and Json to Object",
        long_description=long_description,
        long_description_content_type='text/markdown',
        url="https://github.com/koffiisen/SmartJson",
        keywords=['Json', 'Class', 'Object to json', 'Class to json',
                  'json to object', 'json to class', 'Tool', 'convert Class',
                  'Python libraries to convert class to json', 'library to convert class to json python',
                  'object and dict', 'to Json', 'Json to Object',
                  'Class', 'date', 'datetime', 'set',
                  'OrderedDict', 'deque', 'list', 'enum',
                  'int', 'float', 'bool', 'complex', 'tuple', 'str',
                  'dict', 'bytes', 'None'],
        packages=find_packages(),
        python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*', # Adjusted based on common six usage, can be broader if needed
        install_requires=[
            'six>=1.10.0',
            'enum34; python_version<"3.4"', # For Enum support in Python < 3.4
        ],
        include_package_data=False,
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            # "Programming Language :: Python :: 3.1", # Often skipped
            # "Programming Language :: Python :: 3.2", # Often skipped
            # "Programming Language :: Python :: 3.3", # Often skipped
            # "Programming Language :: Python :: 3.4", # Often skipped
            # "Programming Language :: Python :: 3.5", # Often skipped
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
