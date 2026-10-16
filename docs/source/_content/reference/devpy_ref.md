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

Setup options include `venv`, `hooks`, and `private` where private dependencies are configured.
