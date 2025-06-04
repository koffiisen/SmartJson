# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - YYYY-MM-DD
*(User will need to replace YYYY-MM-DD with the actual release date)*

### Added
- **Schema Validation**: Implemented comprehensive schema validation for both serialization and deserialization.
  - Users can define schemas using Python dictionaries to specify expected types, required fields, and nested structures.
  - Validation is triggered by passing a `schema` argument to `serialize()`, `serializeToJsonFile()`, `toObject()`, and `toObjectFromFile()`.
  - Introduces `SmartJsonSchemaValidationError` for detailed error reporting.
- **`examples/` Directory**: Created a new `examples/` directory with detailed example scripts:
  - `01_basic_serialization_deserialization.py`
  - `02_nested_data_and_types.py`
  - `03_schema_validation_demo.py`
  - `04_file_operations.py`
- **GitHub Actions Workflows**:
  - CI workflow (`ci.yml`) for automated testing across Python 2.7, 3.6-3.11.
  - Release workflow (`release.yml`) to build and create GitHub releases on tagged commits.
  - Release Drafter workflow (`release-drafter.yml`) and configuration (`.github/release-drafter.yml`) to automate drafting of release notes.
- **CI Status Badge**: Added a GitHub Actions CI status badge to `README.md`.

### Changed
- **Python Compatibility**:
  - Major overhaul to ensure compatibility with Python 2.7 and Python 3.6+.
  - Integrated `six` library for handling version differences (e.g., string types, iterators).
  - Updated file I/O to use `io.open` with UTF-8 encoding for consistent behavior.
  - Added `enum34` dependency in `setup.py` for Python versions older than 3.4 to support `Enum`.
- **Project Structure**:
  - Renamed the internal `scripts` folder to `smartjson` to follow standard Python packaging conventions.
  - Updated all relevant import statements in the library, tests, and examples.
- **Documentation (`README.md`)**:
  - Complete rewrite and restructuring for improved clarity, comprehensiveness, and user guidance.
  - New sections for Overview, Features, Installation, Quick Start, Core Concepts & Usage, Supported Data Types, Schema Validation details, and Detailed Examples.
- **Top-Level Example (`example.py`)**:
  - Refactored into a concise "Quick Start" guide, directing users to the more detailed scripts in the `examples/` folder.
- **Internal Error Handling**:
  - Refined internal error handling with more specific custom exceptions (`SmartJsonSerializationError`, `SmartJsonDeserializationError`, `SmartJsonCircularDependencyError`, `SmartJsonUnsupportedTypeError`, `SmartJsonSchemaValidationError`) all inheriting from a base `SmartJsonError`.
- **Circular Dependency Detection**:
  - Robust mechanism implemented to detect and report circular dependencies during the serialization process, raising `SmartJsonCircularDependencyError`.

### Fixed
- (This set of tasks primarily focused on new features and refactoring. Any specific bug fixes from prior unversioned work would be listed here based on project history.)

## [2.0.3] - (Previous version)
- (This is a placeholder. Actual changes for 2.0.3 would be listed here based on project history. For the current exercise, 2.1.0 is the focus.)

---
*Note to user: Please replace YYYY-MM-DD with the actual release date for version 2.1.0.*
