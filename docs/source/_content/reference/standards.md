# Standards

## Code Standards

```{seealso}
[Linting, Formatting and Type Checking](../user_guide/linting.md)
```

To ensure consistency, maintainability, and code quality across the project, all contributions should comply with the following standards and tooling requirements:

Code must be formatted using **Black**. Black enforces a consistent style and should be considered the source of truth for code formatting.

```bash
black .
```

Imports must be organised using **isort**. This ensures a consistent and readable import structure across the codebase.

```bash
isort .
```

Code should pass all **Flake8** checks before being submitted for review. Flake8 is used to identify style violations, potential bugs, and other code quality issues.

```bash
flake8 .
```

Where type hints are present, code should pass **MyPy** type checking. New code should include type annotations where practical to improve maintainability and developer tooling support.

```bash
mypy src/
```

Where available (see [Linting, Formatting and Type Checking](../user_guide/linting.md)), automated CI checks will enforce these standards and must pass before changes can be merged.

## Documentation Standards

Documentation should be maintained alongside the codebase and updated whenever changes affect user-facing behaviour, configuration, or workflows. New features should not be considered complete until any required documentation has been added or updated.

Documentation should be clear, concise, and written for its intended audience. Content should follow the [Diátaxis framework](https://diataxis.fr/start-here/), ensuring tutorials, how-to guides, reference material, and explanations each serve a distinct purpose.

Examples and code snippets should be accurate, up to date, and reflect recommended usage patterns.

### In-Code Documentation
```{seealso}
[How to build the documentation](../user_guide/build_docs.md)
```
Docstrings should be provided for all modules, classes and functions.
They should include a short description along with parameters, purpose, and return values.

Comments should be used sparingly, prioritising adding context to explain *why* rather than *what*.
