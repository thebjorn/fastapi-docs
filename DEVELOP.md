# Development Guide for fastapi_docs
This document provides guidelines for developing and testing the fastapi_docs package.

## Setting Up the Development Environment

We use a dedicated virtual environment to run tests and manage dependencies.
The virtualenv will be named after the package name and python version, e.g. fastapi_docs311 for fastapi_docs running on Python 3.11.
The virtualenvs are located at `/srv/venv`, e.g. `/srv/venv/fastapi_docs311`.

To create the virtualenv, run the following command:

```bash
dk testpackage
```

This command will create the virtualenv and install all necessary dependencies, and run initial tests to verify the setup.

Indiviual tools installed in the virtualenv can be ran (without activiating the virtualenv), by specifying the full path to the tool, e.g. `/srv/venv/fastapi_docs311/Scripts/pytest` to run pytest.

## Running Tests

It is important that you clear the DJANGO_SETTINGS_MODULE environment variable before running tests.
Then run tests using pytest from the virtualenv:

```bash
/srv/venv/fastapi_docs311/Scripts/pytest tests    # run all tests
/srv/venv/fastapi_docs311/Scripts/pytest tests/test_specific_file.py    # run tests in a specific file
/srv/venv/fastapi_docs311/Scripts/pytest -k "test_function_name"    # run a specific test function
/srv/venv/fastapi_docs311/Scripts/pytest --cov=fastapi_docs tests    # run tests with coverage report
```

## Code Quality and Linting

We use pep8 and pylint to ensure code quality and adherence to coding standards.
To run pep8 and pylint, use the following commands:

```bash
dk pep8
dk pylint
```

## Coding Standards
Follow the instructions in STYLEGUIDE.md for coding standards and best practices.

## Test coverage
Write tests for all new features and bug fixes.
Aim for high test coverage and use coverage reports to identify untested code paths.

# Documentation
Maintain up-to-date documentation for all public APIs and modules.
Use docstrings and comments to explain complex logic and design decisions.

## Development Tasks
Create standard status files

- TODO.md for high level tasks
- TASKS.md for detailed implementation guidance
- STATUS.md for project health metrics
- SESSIONS.md for LLM session logs