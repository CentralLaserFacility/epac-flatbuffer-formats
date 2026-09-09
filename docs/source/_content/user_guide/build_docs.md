# How to build the documentation

Documentation is built with `Sphinx` in this project, with the API reference generated from docstrings in the source code using `autodoc2`.

The design and structure of the documentation is outlined in [this section](../explanations/structure.md) of the docs.

## Manual build
To build the documentation manually, run:

```shell
$ ./dev.py doc
```

This will build the documentation, with a fresh environment (without cached values), in `docs/build/html` from the `docs/source` directory.

This is the command used to generate documentation in the release workflow. See [here for more information](../user_guide/releasing.md).

## Auto build

`sphinx-autobuild` is included by default and can be used to rebuild when changes are observed in the `src/` or `docs/` directories. Run:

```shell
$ ./dev.py local-doc
```

Like the manual build, this will build the documentation in `docs/build/html` from the `docs/source` directory.

Additionally, this will serve your documentation locally at [127.0.0.1:8000](http://127.0.0.1:8000) which should update automatically.

````{note}
`sphinx-autobuild` uses caching, which may prevent some changes from appearing immediately. If updates are not reflected in the generated documentation, force a full rebuild by running Sphinx with a fresh environment:
```shell
$ sphinx-build -E docs/source/ docs/build/html
```
The `-E` option ignores the saved environment and rebuilds all documentation from scratch.
````
