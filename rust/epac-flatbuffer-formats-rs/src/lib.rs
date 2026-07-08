use pyo3::prelude::*;

#[rustfmt::skip]
#[allow(unused_imports, dead_code, clippy::all, mismatched_lifetime_syntaxes)]
#[path = "generated/pva0_generated.rs"]
pub mod pva0;
mod types;
#[pymodule]
mod epac_flatbuffer_formats_rs {
    use pyo3::prelude::*;
    use crate::pva0;

    #[pyfunction]
    fn flatbuffer_roundtrip_check() -> PyResult<bool> {
        let mut builder = flatbuffers::FlatBufferBuilder::new();
        let b = pva0::Bool::create(&mut builder, &pva0::BoolArgs { value: true });
        builder.finish(b, None);
        let buf = builder.finished_data();
        let parsed = flatbuffers::root::<pva0::Bool>(buf).unwrap();
        Ok(parsed.value())
    }

    use crate::types::TimeT;

    #[pyfunction]
    fn serialise_time(time_t: TimeT) -> PyResult<Vec<u8>> {
        let mut builder = flatbuffers::FlatBufferBuilder::new();
        let offset = time_t.serialise(&mut builder);
        builder.finish(offset, None);
        Ok(builder.finished_data().to_vec())
    }

    use crate::types::AlarmT;

    #[pyfunction]
    fn serialise_alarm(alarm: AlarmT) -> PyResult<Vec<u8>> {
        let mut builder = flatbuffers::FlatBufferBuilder::new();
        let offset = alarm.serialise(&mut builder);
        builder.finish(offset, None);
        Ok(builder.finished_data().to_vec())
    }

    use crate::types::DisplayT;

    #[pyfunction]
    fn serialise_display(display: DisplayT) -> PyResult<Vec<u8>> {
        let mut builder = flatbuffers::FlatBufferBuilder::new();
        let offset = display.serialise(&mut builder);
        builder.finish(offset, None);
        Ok(builder.finished_data().to_vec())
    }

    use crate::types::ControlT;

    #[pyfunction]
    fn serialise_control(control: ControlT) -> PyResult<Vec<u8>> {
        let mut builder = flatbuffers::FlatBufferBuilder::new();
        let offset = control.serialise(&mut builder);
        builder.finish(offset, None);
        Ok(builder.finished_data().to_vec())
    }


    use crate::types::AnyScalar;

    #[pyfunction]
    fn serialise_any(value: AnyScalar) -> PyResult<Vec<u8>> {
        let mut builder = flatbuffers::FlatBufferBuilder::new();
        let offset = value.serialise(&mut builder);
        builder.finish(offset, None);
        Ok(builder.finished_data().to_vec())
    }

    use crate::types::NTScalarAny;

    #[pyfunction]
    fn serialise_ntscalarany(nt: NTScalarAny) -> PyResult<Vec<u8>> {
        let mut builder = flatbuffers::FlatBufferBuilder::new();
        let offset = nt.serialise(&mut builder);
        builder.finish(offset, None);
        Ok(builder.finished_data().to_vec())
    }

    // use crate::types::IntArrayT;

    // #[pyfunction]
    // fn serialise_int_array(arr: IntArrayT) -> PyResult<Vec<u8>> {
    //     let mut builder = flatbuffers::FlatBufferBuilder::new();
    //     let offset = arr.serialise(&mut builder);
    //     builder.finish(offset, None);
    //     Ok(builder.finished_data().to_vec())
    // }
    use crate::types::AnyArray;

    #[pyfunction]
    fn serialise_any_array(arr: AnyArray) -> PyResult<Vec<u8>> {
        let mut builder = flatbuffers::FlatBufferBuilder::new();
        let offset = arr.serialise(&mut builder);
        builder.finish(offset, None);
        Ok(builder.finished_data().to_vec())
    }
}
