use pyo3::prelude::*;

#[rustfmt::skip]
#[allow(warnings)]
#[allow(clippy::all)]
#[path="generated/pva0_generated.rs"] // this is the flatbuffer automatically generated module
mod pva0_generated;
#[allow(clippy::enum_variant_names)]
mod pva0_data;
pub mod serialise;

#[pymodule]
mod epac_flatbuffer_formats_rs {

    use super::pva0_data::PVData;
    use crate::serialise::Serialise;
    use pyo3::prelude::*;
    use pyo3::{types::PyBytes, PyResult};

    const FILE_IDENTIFIER: &str = "pva0";

    #[pyfunction]
    pub fn serialise_pv_data(py: Python<'_>, data: PVData) -> PyResult<Py<PyBytes>> {
        let mut builder = flatbuffers::FlatBufferBuilder::with_capacity(1024);
        let obj = data.serialise(&mut builder);
        builder.finish(obj, Some(FILE_IDENTIFIER));
        Ok(PyBytes::new(py, builder.finished_data()).unbind())
    }
}
