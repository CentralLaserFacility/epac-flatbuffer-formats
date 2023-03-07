#!/usr/bin/env python3

import argparse
import os
import shutil
import stat
import subprocess
import sys


# == Framework ==


SETUP_MAP = {}
COMMAND_MAP = {}


def setup(name):
    """Declare a class as a "setup" option.

    The class must provide the following methods, which must be decorated as
    @classmethod or @staticmethod:

     - `is_setup`: returns a bool indicating whether the setup has been run
     - `setup`: do the setup. May assume that `is_setup()` is false
     - `clean`: undo the setup. May assume that `is_setup()` is true

    The doc string will be used as command-line help.
    """

    def inner(cls):
        SETUP_MAP[name] = cls
        return cls

    return inner


def command(name):
    """Declare a function as a command.

    The function will be called with no arguments.

    The doc string will be used as command-line help.
    """

    def inner(func):
        COMMAND_MAP[name] = func
        return func

    return inner


def run_cmd(executable, *args, **kwargs):
    """Run a command.

    Since this doesn't run a command in a venv, for most purposes you should prefer:
    ```python
    require("venv").run_cmd(...)
    ```
    """

    kw = dict(check=True)
    kw.update(kwargs)
    env = kwargs.get("env", os.environ)
    path = env["PATH"]
    # On Windows, the behaviour of subprocess.run() is to search the *current*
    # PATH, and the env argument does not override that. So we need to do the
    # search ourselves.
    executable = shutil.which(executable, path=path)
    subprocess.run([executable, *args], **kw)


def require(setup_name: str, *, auto_setup: bool = False):
    """Require that a setup step has been completed.

    This will produce a clean error if the stated setup step hasn't been done.
    Will return the setup class, so you can access class methods on it.
    """

    setup = SETUP_MAP[setup_name]
    if not setup.is_setup():
        if auto_setup:
            run_setup(setup_name, False)
        else:
            error(f"{setup_name} is not set up")
    return setup


# == Configurables ==
# If you want to change these for a particular project, it is recommended that
# you redefine them in the user section below


def packages():
    """Top-level packages, for use with e.g. pdoc."""

    for pkg in os.listdir("src"):
        if pkg.isidentifier():
            yield pkg


def mypy_check_paths():
    """Paths to be checked with mypy."""

    return ["src", "tests"]


def api_doc_modules():
    """Arguments (paths, modules, files) to be passed to pdoc."""

    return packages()


# == Built-in commands and setups ==


@setup("venv")
class SetupVenv:
    """Manage a development environment in .venv"""

    VENV_DIR = ".venv"

    @classmethod
    def is_setup(cls):
        return os.path.isdir(cls.VENV_DIR)

    @classmethod
    def clean(cls):
        shutil.rmtree(cls.VENV_DIR)

    @classmethod
    def setup(cls):
        interpreter = sys.executable
        run_cmd(interpreter, "-m", "venv", cls.VENV_DIR, "--prompt", cls.venv_name())
        # Need pip >= 22 to install in editable mode
        cls.run_cmd("python", "-m", "pip", "install", "pip>=22.0.0")
        cls.run_cmd("pip", "install", "-e", ".[dev]")

    @staticmethod
    def venv_name():
        return os.path.basename(os.getcwd())

    @classmethod
    def venv_bin_path(cls):
        bin_dir_name = "Scripts" if sys.platform.startswith("win32") else "bin"
        path = os.path.join(os.getcwd(), cls.VENV_DIR, bin_dir_name)
        assert os.path.isdir(path)
        return path

    @classmethod
    def run_cmd(cls, *args, **kwargs):
        env = os.environ
        path = env.get("PATH", "")
        env["PATH"] = cls.venv_bin_path() + os.pathsep + path

        run_cmd(*args, **kwargs, env=env)


@setup("hooks")
class SetupHooks:
    """Set up git hooks."""

    HOOKS = {
        "pre-commit": """
#!/bin/bash

DEV=./dev.py

if [ ! -x $DEV -o {os} = win ]; then
    DEV="python $DEV"
fi

STASH_LEN_BEFORE=$(git stash list | wc -l)
git stash push -quk
STASH_LEN_AFTER=$(git stash list | wc -l)

$DEV pre-commit
RESULT=$?

if [ $STASH_LEN_BEFORE -ne $STASH_LEN_AFTER ]; then
    git stash pop -q
fi

exit $RESULT
""",
    }

    @classmethod
    def is_setup(cls):
        for hook in cls.HOOKS:
            if not os.path.exists(os.path.join(".git", "hooks", hook)):
                return False
        return True

    @classmethod
    def clean(cls):
        for hook in cls.HOOKS:
            hook_path = os.path.join(".git", "hooks", hook)
            if os.path.exists(hook_path):
                os.remove(hook_path)

    @classmethod
    def setup(cls):
        for hook, hook_template in cls.HOOKS.items():
            my_os = "win" if sys.platform.startswith("win32") else "unix"
            hook_text = hook_template.format(os=my_os)
            hook_path = os.path.join(".git", "hooks", hook)
            if not os.path.exists(hook_path):
                with open(hook_path, "w") as f:
                    f.write(hook_text.lstrip())
                if not sys.platform.startswith("win32"):
                    mode = os.stat(hook_path).st_mode
                    mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                    os.chmod(hook_path, mode)


@command("pre-commit")
def cmd_precommit():
    """Run pre-commit hooks."""

    venv = require("venv")

    venv.run_cmd("git", "diff", "--staged", "--check")
    venv.run_cmd("black", "--quiet", "--check", "--diff", ".")
    venv.run_cmd("flake8", ".")


@command("fmt")
def cmd_fmt():
    """Format code with black."""

    venv = require("venv")

    venv.run_cmd("black", ".")


@command("test")
def cmd_test():
    """Run test steps."""

    venv = require("venv")

    venv.run_cmd("mypy", *mypy_check_paths())
    venv.run_cmd("pytest")


@command("api-docs")
def cmd_api_docs():
    """Browse API docs."""

    venv = require("venv")

    venv.run_cmd("pdoc", *api_doc_modules())


# == User commands, setups, and other customisations ==


# == Runtime ==


def run_setup(setup_name: str, rerun: bool) -> None:
    setup = SETUP_MAP[setup_name]
    if setup.is_setup():
        if rerun:
            run_clean(setup_name)
        else:
            print("Skipping", setup_name)
            return

    print("Running", setup_name, "... ", end="")
    sys.stdout.flush()
    setup.setup()
    print("done")


def run_clean(setup_name: str) -> None:
    setup = SETUP_MAP[setup_name]
    if not setup.is_setup():
        print("Skipping", setup_name)
        return

    print("Cleaning", setup_name, "... ", end="")
    sys.stdout.flush()
    setup.clean()
    print("done")


def main():
    parser = argparse.ArgumentParser(
        description="Script for setting up and using a development environment"
    )
    commands = parser.add_subparsers(
        dest="command", required=True, help="command to run", metavar="CMD"
    )

    setup = commands.add_parser("setup", help="Run a setup step")
    setup_choices = setup.add_subparsers(
        dest="setup", required=True, help="setup to run", metavar="SETUP"
    )
    clean = commands.add_parser("clean", help="Run a cleanup step")
    clean_choices = clean.add_subparsers(
        dest="setup", required=True, help="cleanup to run", metavar="CLEANUP"
    )

    setup_choices.add_parser("all", help="Run all setup steps")
    clean_choices.add_parser("all", help="Run all cleanup steps")

    for setup_name, setup_cls in SETUP_MAP.items():
        doc = setup_cls.__doc__
        if doc:
            first_line = doc.splitlines()[0]
        else:
            doc = ""
            first_line = ""
        setup_choices.add_parser(setup_name, help=first_line, description=doc)
        clean_choices.add_parser(setup_name, help=first_line, description=doc)

    for cmd_name, cmd_func in COMMAND_MAP.items():
        doc = cmd_func.__doc__
        if doc:
            first_line = doc.splitlines()[0]
        else:
            doc = ""
            first_line = ""
        commands.add_parser(cmd_name, help=first_line, description=doc)

    setup.add_argument(
        "-r", "--rerun", action="store_true", help="Clean first if already set up"
    )

    run = commands.add_parser("run", help="Run a command in the venv")
    run.add_argument("run_args", nargs=argparse.REMAINDER, help="Command to run")

    args = parser.parse_args()

    try:
        main_inner(args)
    except subprocess.CalledProcessError as exc:
        error(f"command failed: {' '.join(exc.cmd)}")


def error(err_str: str):
    print("ERROR:", err_str, file=sys.stderr)
    sys.exit(1)


def main_inner(args):
    cmd = args.command
    if cmd == "setup":
        setup_name = args.setup
        if setup_name == "all":
            for setup in SETUP_MAP:
                run_setup(setup, args.rerun)
        else:
            run_setup(setup_name, args.rerun)
    elif cmd == "clean":
        setup_name = args.setup
        if setup_name == "all":
            for setup in SETUP_MAP:
                run_clean(setup)
        else:
            run_clean(setup_name)
    elif cmd == "run":
        venv = require("venv")
        venv.run_cmd(*args.run_args)
    else:
        COMMAND_MAP[cmd]()


if __name__ == "__main__":
    main()
