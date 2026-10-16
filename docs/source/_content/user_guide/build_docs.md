# How to build the documentation

Documentation is built with [`Sphinx`][sphinx] in this project, with the API reference generated from docstrings in the source code using [`autodoc2`](https://sphinx-autodoc2.readthedocs.io/en/latest/).

The design and structure of the documentation is outlined in [this section](../reference/structure.md) of the docs.

```{note}
`cargo doc` is used to build the rust API docs when building both manually and automatically.

They are then made available via a static subsite linked in the `Reference` section of the [`Sphinx`][sphinx] built docs.
See [here](rust-api).
```

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

````{warning}
`sphinx-autobuild` uses caching, which may prevent some changes from appearing immediately. If updates are not reflected in the generated documentation, force a full rebuild by running:
```shell
$ ./dev.py doc
```
````

[sphinx]: https://www.sphinx-doc.org/en/master/index.html