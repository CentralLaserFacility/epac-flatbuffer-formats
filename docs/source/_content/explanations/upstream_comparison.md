# Comparison with upstream for f142 and ADAr

The "upstreams" for this project are two ESS projects:
[`streaming-data-types`][streaming-data-types] and
[`python-streaming-data-types`][python-streaming-data-types]. Specific schemas
that will or might be used in EPAC have been copied into this repository, to
which EPAC-specific schemas have been added. This repository then serves as a
canonical location for all the schemas used in EPAC.

Unlike upstream, the Python support code is stored in the same repository, which
helps keep our generated code in sync with the schema definitions. The Python
code taken from upstream has been modified as necessary to pass our CI steps.

Where there is overlap, we aim to maintain compatibility with upstream, so that
any code using the Python [`streaming_data_types`][python-streaming-data-types]
package (`ess-streaming-data-types` on PyPI) can be adapted to use this package
with little effort beyond changing the import paths.

At the time of writing,
[`python-streaming-data-types`][python-streaming-data-types] allows strings and
string arrays to be serialised to `f142`. However, as the string variants have been
removed from the [`streaming-data-types`][streaming-data-types] version of the
`f142` schema, we have also removed support for string serialisation.


[streaming-data-types]: https://github.com/ess-dmsc/streaming-data-types
[python-streaming-data-types]: https://github.com/ess-dmsc/python-streaming-data-types