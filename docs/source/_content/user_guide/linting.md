# Linting, Formatting and Type Checking

> *This section details the tools used to ensure code quality.*

## Tools

Several tools are used in this project to enforce code quality:

- [`mypy`](https://mypy.readthedocs.io/en/stable/) - performs static type checking using Python type annotations
- [`Black`](https://black.readthedocs.io/en/stable/) - automatically formats Python code to a consistent style
- [`Flake8`](https://flake8.pycqa.org/en/latest/) - performs static code analysis to identify style and syntax issues
- [`isort`](https://isort.readthedocs.io/en/latest/) - automatically sorts and groups import statements to align with conventions

Together, these tools help enforce coding standards, consistency, and readability throughout the codebase. They support long-term maintainability, enable early issue detection, and are integrated into the CI pipeline to ensure quality checks are applied automatically to all changes.

## Using the tools

`black` and `isort` can be run using
```shell
$ ./dev.py fmt
```
while `flake8` is run as part of the pre-commit hooks, which are runnable manually with
```shell
$ ./dev.py pre-commit
```


Additionally, `mypy` will also be run on files in `src/` and `tests/` (along with `dev.py`) when tests are run with:
```
$ ./dev.py test
```

Code standards for this project are detailed in the [reference](../reference/standards.md).