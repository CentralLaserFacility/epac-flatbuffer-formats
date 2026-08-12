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

    return [
        "src",
        "tests",
        "rust/epac-flatbuffer-formats-rs/python/epac_flatbuffer_formats_rs",
        "rust/epac-flatbuffer-formats-rs/python/tests",
    ]


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

PATCH_FILE=$(mktemp)

git diff --ignore-submodules --binary --exit-code --no-color --no-ext-diff >$PATCH_FILE
UNSTAGED_CHANGES=$?

if [ $UNSTAGED_CHANGES -ne 0 ]; then
    git checkout --no-recurse-submodules -- .
fi

$DEV pre-commit
RESULT=$?

if [ $UNSTAGED_CHANGES -ne 0 ]; then
    git apply --whitespace=nowarn $PATCH_FILE
fi

rm $PATCH_FILE

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


# edited from base to include rust hooks
@command("pre-commit")
def cmd_precommit():
    """Run pre-commit hooks."""
    # base hooks for python
    venv = require("venv")

    venv.run_cmd("git", "diff", "--staged", "--check")
    venv.run_cmd("black", "--quiet", "--check", "--diff", ".")
    venv.run_cmd("flake8", ".")

    # rust hooks if toolchain present
    if _has_rust_toolchain(venv):
        venv.run_cmd(
            "cargo",
            "fmt",
            "--manifest-path",
            "./rust/Cargo.toml",
            "--all",
            "--check",
        )
        venv.run_cmd(
            "cargo",
            "clippy",
            "--manifest-path",
            "./rust/Cargo.toml",
            "--all-targets",
            "--all-features",
            "--",
            "-Dwarnings",
        )


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

    if _has_rust_toolchain(venv):
        venv.run_cmd("cargo", "test", "-q", "--manifest-path", "./rust/Cargo.toml")


@command("benchmark")
def cmd_benchmark():
    """Run benchmarking tests."""

    venv = require("venv")

    venv.run_cmd("pytest", "benchmarks")


@command("api-docs")
def cmd_api_docs():
    """Browse API docs."""

    venv = require("venv")

    venv.run_cmd("pdoc", *api_doc_modules())


# == User commands, setups, and other customisations ==


def _has_rust_toolchain(venv) -> bool:
    """Verify that a rust toolchain exists"""

    if not shutil.which("rustc"):
        return False

    if not shutil.which("cargo"):
        return False

    try:
        venv.run_cmd(
            "rustc",
            "--version",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        return False


@setup("flatc")
class SetupFlatc:
    """Install the correct version of flatc into the venv"""

    VENV_CLASS = SetupVenv

    SCHEMA_SOURCE_PATH = "schemas/"
    GENERATED_CODE_PATH = "src/epac/flatbuffers/fbschemas"
    RUST_GENERATED_CODE_PATH = "rust/epac-flatbuffer-formats-rs/src/generated"

    @classmethod
    def is_setup(cls):
        venv = cls.VENV_CLASS
        return venv.is_setup() and os.path.isfile(cls.flatc_exe_path())

    @classmethod
    def clean(cls):
        if os.path.exists(cls.flatc_exe_path()):
            os.remove(cls.flatc_exe_path())

    @classmethod
    def setup(cls):
        import io
        import zipfile
        from urllib.request import urlopen

        venv = cls.VENV_CLASS
        if not venv.is_setup():
            error("Must run setup for venv before flatc")

        version = cls.flatc_version()

        flatc_release_url = "https://github.com/google/flatbuffers/releases/download/"
        flatc_release_url += f"v{version}/"

        if sys.platform.startswith("win32"):
            flatc_release_url += "Windows.flatc.binary.zip"
            flatc_file_name = "flatc.exe"
            chmod = False
        else:
            flatc_release_url += "Linux.flatc.binary.g++-10.zip"
            flatc_file_name = "flatc"
            chmod = True

        with urlopen(flatc_release_url) as f:
            flatc_zip_data = f.read()

        flatc_zip = zipfile.ZipFile(io.BytesIO(flatc_zip_data))
        with flatc_zip.open(flatc_file_name) as zf:
            flatc_data = zf.read()

        with open(cls.flatc_exe_path(), "wb") as f:
            f.write(flatc_data)

        if chmod:
            mode = os.stat(cls.flatc_exe_path()).st_mode & 0o777
            mode_read = mode & 0o444
            mode_exe = mode_read >> 2
            os.chmod(cls.flatc_exe_path(), mode | mode_exe)

    @classmethod
    def flatc_exe_path(cls):
        venv = cls.VENV_CLASS
        ext = ".exe" if sys.platform.startswith("win32") else ""
        return os.path.join(venv.venv_bin_path(), f"flatc{ext}")

    @staticmethod
    def flatc_version():
        """Try to guess the correct flatbuffers version from pyproject.toml."""

        import re

        flatbuffers_version_re = re.compile(r'"flatbuffers==([\d\.]+)"')
        candidates = set()
        with open("pyproject.toml") as f:
            for line in f:
                m = flatbuffers_version_re.search(line)
                if m:
                    candidates.add(m.group(1))

        if len(candidates) != 1:
            raise RuntimeError("could not guess flatc version from pyproject.toml")

        return list(candidates)[0]

    @classmethod
    def run(cls, *args, **kwargs):
        venv = cls.VENV_CLASS
        venv.run_cmd("flatc", *args, **kwargs)


@command("schema-generate")
def cmd_schema_generate() -> None:
    """Generate Python and Rust code from schema files."""

    flatc: SetupFlatc = require("flatc")
    venv: SetupVenv = require("venv")

    for fname in os.listdir(flatc.SCHEMA_SOURCE_PATH):

        base, ext = os.path.splitext(fname)

        # generate python code for all schemas
        if ext == ".fbs":
            dest_dir = os.path.join(flatc.GENERATED_CODE_PATH, base)
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
            os.mkdir(dest_dir)

            flatc.run(
                "-p",
                "--python-typing",
                "-o",
                dest_dir,
                os.path.join(flatc.SCHEMA_SOURCE_PATH, fname),
            )

            # Stupid flatc can't generate relative imports
            for file in os.listdir(dest_dir):
                if file.endswith(".py"):
                    convert_to_relative_imports(os.path.join(dest_dir, file))
            venv.run_cmd("black", "--quiet", dest_dir)

        # generate rust code for Pva0 schema
        if fname == "pva0.fbs":
            dest_dir = flatc.RUST_GENERATED_CODE_PATH
            generated_file = os.path.join(dest_dir, f"{base}_generated.rs")

            if os.path.exists(generated_file):
                os.remove(generated_file)

            os.makedirs(dest_dir, exist_ok=True)

            flatc.run(
                "--rust",
                "-o",
                dest_dir,
                os.path.join(flatc.SCHEMA_SOURCE_PATH, fname),
            )


def convert_to_relative_imports(file):
    # flatc generates files with absolute imports to neighbouring files
    # Since it doesn't know which package the code appears in, this clearly
    # doesn't work
    # The intended workflow appears to be to place the entire package path into
    # the fbs file as a namespace directive, but at least the first part of this
    # seems like it should belong to the build system

    # This function will rewrite any suspicious absolute imports it finds into
    # relative imports. Currently it looks for module names starting with
    # capital letters, but this may need to be changed

    import re

    absolute_import_re = re.compile(
        r"(?P<whitespace>\s*)from (?P<module_name>[A-Z][a-zA-Z_\.]*) "
        r"import (?P<attribute_names>.+)$"
    )
    relative_import_template = (
        r"\g<whitespace>from .\g<module_name> import \g<attribute_names>\n"
    )
    lines = []
    converted = False
    with open(file) as f:
        for line in f:
            m = absolute_import_re.match(line)
            if m:
                lines.append(m.expand(relative_import_template))
                converted = True
            else:
                lines.append(line)

    if converted:
        with open(file, "w") as f:
            f.writelines(lines)


@command("rust-develop")
def cmd_rust_develop() -> None:
    """Install the Rust extension in editable mode with maturin."""
    rs_bindings: SetupRustBindings = require("rust-bindings")
    rs_bindings.develop()


@command("rust-build")
def cmd_rust_build() -> None:
    """
    Build a release wheel for the Rust extension with maturin.

    Default location is "rust/build".
    """
    # don't require setup
    rs_bindings = SetupRustBindings()
    rs_bindings.build("-o", "rust/build")


@command("rust-clean")
def cmd_rust_clean() -> None:
    """Uninstall the Rust extension from the active venv."""
    rs_bindings: SetupRustBindings = require("rust-bindings")
    rs_bindings.clean()


@command("rust-stubs")
def cmd_rust_stubs() -> None:
    """
    Generate python stubs for rust bindings

    This feature is still in active development
    (See https://pyo3.rs/main/type-stub) and should be used as an aid only.

    Manual editing of generated stubs files is recommended.
    """
    rs_bindings: SetupRustBindings = require("rust-bindings")
    rs_bindings.generate_stubs()


@setup("rust-bindings")
class SetupRustBindings:

    VENV_CLASS = SetupVenv
    BUILD_PATH = "./rust/epac-flatbuffer-formats-rs/"
    MODULE_NAME = "epac_flatbuffer_formats_rs"
    DISTRIBUTION_NAME = "epac-flatbuffer-formats-rs"

    @classmethod
    def is_setup(cls) -> bool:

        venv = cls.VENV_CLASS
        if not venv.is_setup():
            return False

        # confirm maturin is installed
        try:
            venv.run_cmd("maturin", "--version", check=True, stdout=subprocess.DEVNULL)
        except Exception:
            error("maturin not available, install with pip or setup venv")

        # soft checking whether the module is importable
        try:
            import epac_flatbuffer_formats_rs  # noqa: F401
        except Exception:
            return False

        return True

    @classmethod
    def setup(cls) -> None:
        venv = cls.VENV_CLASS
        if not venv.is_setup():
            error("Must run setup for venv first")

        # develop and install bindings module
        cls.develop()

    @classmethod
    def build(cls, *args) -> None:
        """Run maturin build in release mode"""
        venv = cls.VENV_CLASS
        venv.run_cmd(
            "maturin",
            "build",
            *args,
            "--release",
            "--manifest-path",
            cls.manifest_path(),
        )

    @classmethod
    def develop(cls, *args) -> None:
        """Run maturin develop for the active source tree"""
        venv = cls.VENV_CLASS
        venv.run_cmd(
            "maturin",
            "develop",
            *args,
            "--manifest-path",
            cls.manifest_path(),
        )

    @classmethod
    def clean(cls) -> None:
        """
        Uninstall rust-python serialisation bindings module
        """
        venv = cls.VENV_CLASS
        if not cls.is_setup():
            error("Cannot clean, not setup")

        # uninstall bindings module
        try:
            venv.run_cmd("pip", "uninstall", "-y", cls.DISTRIBUTION_NAME)
        except Exception as e:
            error(f"Cannot clean, failed on pip uninstall: {e}")

    @classmethod
    def manifest_path(cls) -> str:
        return os.path.join(cls.BUILD_PATH, "Cargo.toml")

    @classmethod
    def generate_stubs(cls, *args) -> None:
        """Generate stubs for rust/python bindings"""
        venv = cls.VENV_CLASS
        stubs_path = os.path.join(cls.BUILD_PATH, "python", cls.MODULE_NAME)
        venv.run_cmd(
            "maturin",
            "generate-stubs",
            *args,
            "--out",
            stubs_path,
            "--manifest-path",
            cls.manifest_path(),
        )


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
