from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    setup(
        name='smartjson',
        version='0.0.3',
        author="J. Koffi ONIPOH",
        author_email="jolli644@gmail.com",
        description="A tool to convert any class to json and convert json to object",
        long_description=long_description,
        long_description_content_type='text/markdown',
        url="https://github.com/koffiisen/SmartJson",
        keywords=['Json', 'Class', 'Object to json', 'Class to json', 'json to object', 'json to class'],
        packages=find_packages(),
        python_requires='>=2.7',
        include_package_data=False,
        classifiers=[
            "Programming Language :: Python :: 2.7",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
