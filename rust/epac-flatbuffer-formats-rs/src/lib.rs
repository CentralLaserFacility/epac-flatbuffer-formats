use pyo3::prelude::*;


#[rustfmt::skip]
#[allow(warnings)]
#[allow(clippy::all)]
#[path="generated/pva0_generated.rs"] // this is the flatbuffer automatically generated module
pub mod pva0_generated;
mod pva0_data;

#[pymodule]
mod epac_flatbuffer_formats_rs {
    use super::pva0_data::{NTScalarAny, PVData};
    use pyo3::prelude::*;
    use pyo3::{types::PyBytes, PyResult};

    #[pyfunction]
    pub fn serialise_nt_scalar_any(py: Python<'_>, scalar: NTScalarAny) -> PyResult<Py<PyBytes>> {
        let mut builder = flatbuffers::FlatBufferBuilder::with_capacity(1024);
        let obj = scalar.serialise(&mut builder);
        builder.finish(obj, Some("test"));
        Ok(PyBytes::new(py, builder.finished_data()).unbind())
    }

    #[pyfunction]
    pub fn serialise_pv_data(py: Python<'_>, data: PVData) -> PyResult<Py<PyBytes>> {
        let mut builder = flatbuffers::FlatBufferBuilder::with_capacity(1024);
        let obj = data.serialise(&mut builder);
        builder.finish(obj, Some("test"));
        Ok(PyBytes::new(py, builder.finished_data()).unbind())
    }
}
