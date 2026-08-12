use pyo3::prelude::*;

// this is the flatbuffer automatically generated module
#[rustfmt::skip]
#[allow(warnings)]
#[allow(clippy::all)]
#[path="generated/pva0_generated.rs"]
mod pva0_generated;

#[allow(clippy::enum_variant_names)]
pub mod pva0_data; // defines rust data structures
pub mod serialise; // defines the `serialise` trait

/// This module is the entry point for the Python bindings
/// It exposes the `serialise_pv_data` function which takes a python (pydantic) `PVData` object and
/// serialises to python bytes.
///
#[pymodule]
#[pyo3(name = "_bindings")]
pub mod epac_flatbuffer_formats_rs {

    use super::pva0_data::PVData;
    use crate::serialise::Serialise;
    use pyo3::prelude::*;
    use pyo3::{types::PyBytes, PyResult};

    const FILE_IDENTIFIER: &str = "pva0";

    /// Serialise a PVData object to bytes
    ///
    /// _Args_
    /// <p> data - `PVData` object to serialise</p>
    ///
    /// _Returns_
    /// <p> bytes - serialissed flatbuffer bytes</p>
    ///
    /// ---
    /// ## Example:
    ///
    /// ``` python
    /// from epac_flatbuffer_formats_rs import serialise_pv_data
    /// from epac.flatbuffers.data_types import PVData
    ///
    /// data = PVData(...)
    ///
    /// # serialise with rust
    /// payload = serialise_pv_data(data)
    ///
    /// assert len(payload)>0
    /// assert isinstance(payload, bytes)
    /// ```
    ///
    #[pyfunction]
    pub fn serialise_pv_data(py: Python<'_>, data: PVData) -> PyResult<Py<PyBytes>> {
        let mut builder = flatbuffers::FlatBufferBuilder::with_capacity(1024);
        let obj = data.serialise(&mut builder);
        builder.finish(obj, Some(FILE_IDENTIFIER));
        Ok(PyBytes::new(py, builder.finished_data()).unbind())
    }
}
