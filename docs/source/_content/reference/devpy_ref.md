# `.dev.py` Commands

Run `./dev.py --help` for the authoritative command list.

Common commands are:

| Command | Purpose |
|---|---|
| `./dev.py setup all` | Run all setup steps |
| `./dev.py clean all` | Remove all setup steps |
| `./dev.py pre-commit` | Run commit checks |
| `./dev.py fmt` | Format Python code |
| `./dev.py test` | Run mypy and pytest |
| `./dev.py doc` | Generate `Sphinx` documentation |
| `./dev.py local-doc` | Generate and serve `Sphinx` documentation locally |
| `./dev.py run COMMAND` | Run a command in `.venv` |
| `./dev.py rust-develop` | Install the Rust extension in editable mode |
| `./dev.py rust-build` | Build a release wheel for the Rust extension |
| `./dev.py rust-clean` | Uninstall the Rust extension from the active venv |
| `./dev.py rust-stubs` | Generate Python stubs for the Rust bindings |

Set up Rust bindings with `./dev.py setup rust-bindings`. Other setup options
include `venv`, `hooks`, and `flatc`, plus `private` where private dependencies
are configured.
