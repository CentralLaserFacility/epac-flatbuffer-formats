# How to set up the developer environment

> *This is where you write what a developer needs to know to start making changes.*
> *You should start with a description of how to set up a working development environment and maybe some basic information on the structure of the code.*
>
> *The following section covers basic use of the `dev.py` script that is essential to this template.*

## Setup

Common development tasks can be automated using the included `dev.py` script.
To set up a virtual environment for development (in `.venv/`), run:

```shell
$ ./dev.py setup venv
```

Once that has been done, you can use `./dev.py run` to run any command in that
virtual environment. A number of other commands are supported: see `./dev.py
--help`.

To set up a Git pre-commit hook, run:

```shell
$ ./dev.py setup hooks
```

This should prevent you from making commits that fail linting. You can run the
pre-commit checks without making a commit by running:

```shell
$ ./dev.py pre-commit
```

But note that the real pre-commit hook will check the exact code that will be
committed by first stashing any unstaged changes or untracked files, so you
may not get exactly the same results.

## CI (GitHub Actions)

The default CI runs `./dev.py pre-commit` and `./dev.py test` on pushes to or
pull requests against the `development` branch. These run the following tools:

- black
- flake8
- mypy
- pytest

If you want to change this, edit `dev.py`.

The default CI uses a cloud runner. There is also a configuration for a
self-hosted runner, which you can enable if you wish. Pay attention to the
Python versions.

See [here](../reference/standards.md) for more information on code standards.
