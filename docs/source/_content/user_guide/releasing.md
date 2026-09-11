# Releasing

>***NOTE***
>
> The release process is disabled by default. To enable it in a downstream
> project, change `if: false` in the `release-wheel` job of
> `.github/workflows/release.yml` to `if: true` and change
> `PACKAGE_NAME: <name here>` to contain the value of `project.name` in
> `pyproject.toml`.

The skeleton is configured to use `setuptools_scm` by default, and can generate
GitHub releases when you push a version number tag to github. Any tag starting
`v[0-9]` (i.e. `v` followed by any digit) will trigger a release.
`setuptools_scm` will derive a package version from the name of the tag.

To release the version `0.1.1`, for example:
```sh
git tag v0.1.1
git push --tags
```

Generated releases will include a wheel, a source distribution and a
`requirements.txt` file specifying the versions of dependencies that were
installed when the package passed its pre-release tests. This requirements.txt
file should be used as a constraint file when installing the wheel in
production environments, to ensure reproducible installation with a
known-working environment.
