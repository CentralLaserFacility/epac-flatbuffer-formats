# EPAC Data Python skeleton

>**NOTE**
>
>This branch contains template code. For details on how to adopt this template,
>see the `meta` branch.

Change the title and remove the above note. Then replace this paragraph with a
short description of your project.

You might want to add some code snippets to demonstrate what the project does
and how you use it.

## Getting started

This is where you write a description of how to start using the project. This
should start with installation instructions. You can use the following
paragraph.

### Installation

Clone this repository, set up a virtual environment, and run `pip install .`.

## Development

This is where you write what a developer needs to know to start making changes.
You should start with a description of how to set up a working development
environment and maybe some basic information on the structure of the code. The
following section covers basic use of the `dev.py` script that is essential to
this template.

You may also want to include any information needed to contribute to the
repository, such as what branches are used for, any special policies, how CI is
set up, etc.

### Setup

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
