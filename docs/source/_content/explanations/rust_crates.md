(rust-crates)=
# Overview of the Rust crates

The Rust workspace currently contains two crates:


## epac_flatbuffers_derive
This crate defines the `serialise` derive macro, which is used to automatically implement the
serialisation trait for the Rust data structures defined in `epac_flatbuffer_formats_rs`.

The `Serialise` derive generates implementations of the runtime crate's `Serialise` trait
for named-field structs and enums, with attributes for FlatBuffers unions and schema-name differences.

## epac_flatbuffer_formats_rs
This crate defines the Rust data structures and implements the serialisation trait used to write
FlatBuffers. It also exposes the Python binding entry point `serialise_pv_data`.

- `src/` contains the crate's Rust source code:

  - `generated/pva0_generated.rs` contains the FlatBuffers types generated from the `pva0` schema.
  - `serialise.rs` defines the `Serialise` trait and its implementations for primitive, optional,
  string, array, and NumPy values.
  - `pva0_data.rs` defines the Rust representations of PV data and derives Python-object extraction
  and FlatBuffers serialization for them.
  - `any_t.rs` handles dynamically typed scalar and array values, including their FlatBuffers union
  tags.
  - `lib.rs` assembles these modules and exposes the PyO3 `serialise_pv_data` entry point, which
  extracts a Python `PVData`, serializes it into a FlatBuffer, and returns the bytes.

- `python/` contains the bindings' stubs and integration tests.
- `Cargo.toml` is the Crate Manifest
- `pyproject.toml` contains the bindings' build configuration (uses `maturin`).
