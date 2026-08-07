//! This module contains the data structures that are used to represent PVData in Rust.
//! It also implements the `Serialise` trait for these data structures, which allows them to be serialised into flatbuffers.
//!

use crate::pva0_generated as fb;
use crate::serialise::{Discriminant, SerialiseCoerce};
use epac_flatbuffers_derive::Serialise;
use pyo3::prelude::*;
use pyo3::types::PyAny;

use crate::any_t::*;

struct AlarmSeverity(u8);
struct AlarmStatus(u8);
struct DisplayForm(u8);

/// Example macro implement `serialise` for a locally defined unnamed-field wrapper.
macro_rules! impl_serialise_unnamed_fields {
    ($( $ty:ident ),* $(,)?) => {
        $(
            impl crate::serialise::Serialise for $ty {
                type Output<'a> = fb::$ty;
                fn serialise<'a>(
                    &self,
                    _builder: &mut flatbuffers::FlatBufferBuilder<'a>,
                ) -> Self::Output<'a> {
                    fb::$ty(self.0)
                }
            }
        )*
    };
}

/// Example macro to implement `FromPyObject` for a generated type wrapping a u8.
macro_rules! impl_from_pyobject_u8_wrappers {
    ($ty:ty, $err:expr) => {
        impl<'py> FromPyObject<'_, 'py> for $ty {
            type Error = PyErr;
            fn extract(obj: pyo3::Borrowed<'_, 'py, PyAny>) -> PyResult<Self> {
                let value = obj
                    .extract::<u8>()
                    .or_else(|_| obj.getattr("value")?.extract::<u8>())
                    .map_err(|_| pyo3::exceptions::PyTypeError::new_err($err))
                    .unwrap();
                Ok(Self(value))
            }
        }
    };
}

impl_from_pyobject_u8_wrappers!(AlarmSeverity, "unable to extract alarm severity");
impl_from_pyobject_u8_wrappers!(AlarmStatus, "unable to extract alarm status");
impl_from_pyobject_u8_wrappers!(DisplayForm, "unable to extract display form");
impl_serialise_unnamed_fields!(AlarmSeverity, AlarmStatus, DisplayForm);

/// Struct representing an Alarm object.
#[derive(Serialise, FromPyObject)]
struct AlarmT {
    severity: AlarmSeverity,
    status: AlarmStatus,
    message: Option<String>,
}

/// Struct representing a timestamp.
#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
struct TimeT {
    seconds_past_epoch: i64,
    nanoseconds: i32,
    user_tag: i32,
}

/// Struct representing display information.
#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
struct DisplayT {
    limit_low: f64,
    limit_high: f64,
    description: String,
    units: String,
    precision: i32,
    form: DisplayForm,
}

/// Struct representing control information.
#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
struct ControlT {
    limit_low: f64,
    limit_high: f64,
    min_step: f64,
}

/// Struct representing codec information.
#[derive(Serialise, FromPyObject)]
struct CodecT {
    name: String,
}

/// Struct representing a column in a table.
#[derive(Serialise, FromPyObject)]
struct Column {
    value: AnyT,
}

/// Struct representing a dimension in an NDArray.
#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
struct DimensionT {
    size_: i32,
    offset: i32,
    full_size: i32,
    binning: i32,
    reverse: bool,
}

/// Struct representing an NTAttribute.
#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
pub struct NTAttribute {
    name: String,
    value: AnyT,
    tags: Vec<String>,
    descriptor: String,
    alarm: Option<AlarmT>,
    time: Option<TimeT>,
    source_type: i32,
    source: String,
}

/// Struct representing an NTNDArray.
#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
pub struct NTNDArray {
    value: AnyT,
    codec: Option<CodecT>,
    compressed_size: i64,
    uncompressed_size: i64,
    dimension: Vec<DimensionT>,
    unique_id: i32,
    data_time_stamp: Option<TimeT>,
    attribute: Vec<NTAttribute>,
    descriptor: String,
    alarm: Option<AlarmT>,
    time_stamp: Option<TimeT>,
    display: Option<DisplayT>,
}

/// Struct representing an NTScalarAny.
#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
pub struct NTScalarAny {
    value: AnyT,
    descriptor: String,
    alarm: Option<AlarmT>,
    time_stamp: Option<TimeT>,
    display: Option<DisplayT>,
    control: Option<ControlT>,
}

/// Struct representing an NTTable.
#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
pub struct NTTable {
    labels: Vec<String>,
    value: Vec<Column>,
    descriptor: String,
    alarm: Option<AlarmT>,
    time_stamp: Option<TimeT>,
    display: Option<DisplayT>,
}

/// Struct representing XYData.
#[derive(Serialise, FromPyObject)]
pub struct XYData {
    x: NTScalarAny,
    y: NTScalarAny,
}

/// Struct representing a PulseID.
#[derive(Serialise, FromPyObject)]
struct PulseID {
    value: u64,
    #[pyo3(attribute("timestamp"))]
    time_stamp: f64,
}

/// Enum representing the different types of PV data.
#[derive(Serialise, FromPyObject)]
enum PVType {
    NTScalarAny(NTScalarAny),
    NTNDArray(NTNDArray),
    NTTable(NTTable),
    XYData(XYData),
}

/// Struct representing a PVData object.
///
/// The data field is a union type which can be either a scalar, an array, a table or XY data.
#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
pub struct PVData {
    #[serialise(union)]
    data: PVType,
    source_name: String,
    pulse_id: Option<PulseID>,
    effective_time_stamp: Option<TimeT>,
}

#[cfg(test)]
mod tests {
    //! This module contains unit tests for the pva0_data module.
    //!
    //! Unit test strategy is to create object, serialise it and examine manually with generated
    //! flatbuffer code to ensure that the serialisation is correct.
    //!
    //! The verifier is run automatically by the generated code.

    use super::*;

    use crate::pva0_generated::{self as fb};
    use crate::serialise::Serialise;

    #[test]
    fn test_serialise_pv_data_with_scalar() {
        let pv_data = PVData {
            data: PVType::NTScalarAny(NTScalarAny {
                value: AnyT::Scalar(AnyScalar::Double(1.56)),
                descriptor: "test".to_string(),
                alarm: None,
                time_stamp: None,
                display: None,
                control: None,
            }),
            source_name: "source".to_string(),
            pulse_id: Some(PulseID {
                value: 42,
                time_stamp: 1234567890.0,
            }),
            effective_time_stamp: Some(TimeT {
                seconds_past_epoch: 1234567890,
                nanoseconds: 123456789,
                user_tag: 0,
            }),
        };

        let mut builder = flatbuffers::FlatBufferBuilder::with_capacity(1024);
        let obj = pv_data.serialise(&mut builder);
        builder.finish(obj, None);

        let buf = builder.finished_data();
        assert!(!buf.is_empty());

        let pv_data_fb = fb::root_as_pvdata(buf).unwrap();
        assert!(
            pv_data_fb
                .data_as_ntscalar_any()
                .unwrap()
                .value()
                .value_as_double()
                .unwrap()
                .value()
                == 1.56
        );
        assert_eq!(pv_data_fb.data_type(), fb::PVType::NTScalarAny);
        assert_eq!(pv_data_fb.source_name().unwrap(), "source");
        assert_eq!(pv_data_fb.pulse_id().unwrap().value(), 42);
        assert_eq!(pv_data_fb.pulse_id().unwrap().time_stamp(), 1234567890.0);
        assert_eq!(
            pv_data_fb
                .effective_time_stamp()
                .unwrap()
                .seconds_past_epoch(),
            1234567890
        );
        assert_eq!(
            pv_data_fb.effective_time_stamp().unwrap().nanoseconds(),
            123456789
        );
    }

    #[test]
    fn test_serialise_pv_data_with_array() {
        let pv_data = PVData {
            data: PVType::NTNDArray(NTNDArray {
                value: AnyT::Array(AnyArray::DoubleArray(vec![1.0, 2.0, 3.0])),
                codec: None,
                compressed_size: 0,
                uncompressed_size: 0,
                dimension: vec![],
                unique_id: 0,
                data_time_stamp: None,
                attribute: vec![],
                descriptor: "test".to_string(),
                alarm: None,
                time_stamp: None,
                display: None,
            }),
            source_name: "source".to_string(),
            pulse_id: None,
            effective_time_stamp: None,
        };

        let mut builder = flatbuffers::FlatBufferBuilder::with_capacity(1024);
        let obj = pv_data.serialise(&mut builder);
        builder.finish(obj, None);

        let buf = builder.finished_data();
        assert!(!buf.is_empty());

        let pv_data_fb = fb::root_as_pvdata(buf).unwrap();
        assert_eq!(pv_data_fb.data_type(), fb::PVType::NTNDArray);
        assert_eq!(pv_data_fb.source_name().unwrap(), "source");

        let ndarray = pv_data_fb.data_as_ntndarray().unwrap();
        assert_eq!(ndarray.value().value_type(), fb::AnyInner::DoubleArray);
        assert_eq!(ndarray.descriptor().unwrap(), "test");
        assert_eq!(ndarray.compressed_size(), 0);
        assert_eq!(ndarray.uncompressed_size(), 0);
        assert_eq!(ndarray.unique_id(), 0);
    }

    #[test]
    fn test_serialise_nt_scalar_any() {
        let scalar_any = NTScalarAny {
            value: AnyT::Scalar(AnyScalar::Double(1.56)),
            descriptor: "test".to_string(),
            alarm: None,
            time_stamp: None,
            display: None,
            control: None,
        };

        let mut builder = flatbuffers::FlatBufferBuilder::with_capacity(1024);
        let obj = scalar_any.serialise(&mut builder);
        builder.finish(obj, None);

        let buf = builder.finished_data();
        assert!(!buf.is_empty());

        let scalar_any_fb = flatbuffers::root::<fb::NTScalarAny>(buf).unwrap();
        assert_eq!(scalar_any_fb.descriptor().unwrap(), "test");
        assert_eq!(scalar_any_fb.value().value_type(), fb::AnyInner::Double);
        let scalar_value = scalar_any_fb.value().value_as_double().unwrap();
        assert_eq!(scalar_value.value(), 1.56);
    }

    #[test]
    fn test_serialise_nt_ndarray() {
        let ndarray = NTNDArray {
            value: AnyT::Array(AnyArray::DoubleArray(vec![1.0, 2.0, 3.0])),
            codec: None,
            compressed_size: 0,
            uncompressed_size: 0,
            dimension: vec![],
            unique_id: 0,
            data_time_stamp: None,
            attribute: vec![],
            descriptor: "test".to_string(),
            alarm: None,
            time_stamp: None,
            display: None,
        };

        let mut builder = flatbuffers::FlatBufferBuilder::with_capacity(1024);
        let obj = ndarray.serialise(&mut builder);
        builder.finish(obj, None);

        let buf = builder.finished_data();
        assert!(!buf.is_empty());

        let ndarray_fb = flatbuffers::root::<fb::NTNDArray>(buf).unwrap();
        assert_eq!(ndarray_fb.value().value_type(), fb::AnyInner::DoubleArray);
        assert_eq!(ndarray_fb.descriptor().unwrap(), "test");
        assert_eq!(ndarray_fb.compressed_size(), 0);
        assert_eq!(ndarray_fb.uncompressed_size(), 0);
        assert_eq!(ndarray_fb.unique_id(), 0);
    }

    #[test]
    fn test_serialise_nt_table() {
        let table = NTTable {
            labels: vec!["label1".to_string(), "label2".to_string()],
            value: vec![
                Column {
                    value: AnyT::Scalar(AnyScalar::Double(1.0)),
                },
                Column {
                    value: AnyT::Scalar(AnyScalar::Double(2.0)),
                },
            ],
            descriptor: "test".to_string(),
            alarm: None,
            time_stamp: None,
            display: None,
        };

        let mut builder = flatbuffers::FlatBufferBuilder::with_capacity(1024);
        let obj = table.serialise(&mut builder);
        builder.finish(obj, None);

        let buf = builder.finished_data();
        assert!(!buf.is_empty());

        let table_fb = flatbuffers::root::<fb::NTTable>(buf).unwrap();
        let labels = table_fb.labels().unwrap();
        assert_eq!(labels.len(), 2);
        assert_eq!(table_fb.descriptor().unwrap(), "test");

        let columns = table_fb.value();
        assert_eq!(columns.len(), 2);
        let first = columns.get(0);
        let second = columns.get(1);

        let first_any = first.value().unwrap();
        assert_eq!(first_any.value_type(), fb::AnyInner::Double);
        let first_double = first_any.value_as_double().unwrap();
        assert_eq!(first_double.value(), 1.0);

        let second_any = second.value().unwrap();
        assert_eq!(second_any.value_type(), fb::AnyInner::Double);
        let second_double = second_any.value_as_double().unwrap();
        assert_eq!(second_double.value(), 2.0);
    }

    #[test]
    fn test_serialise_xy_data() {
        let xy_data = XYData {
            x: NTScalarAny {
                value: AnyT::Scalar(AnyScalar::Double(1.0)),
                descriptor: "x".to_string(),
                alarm: None,
                time_stamp: None,
                display: None,
                control: None,
            },
            y: NTScalarAny {
                value: AnyT::Scalar(AnyScalar::Double(2.0)),
                descriptor: "y".to_string(),
                alarm: None,
                time_stamp: None,
                display: None,
                control: None,
            },
        };

        let mut builder = flatbuffers::FlatBufferBuilder::with_capacity(1024);
        let obj = xy_data.serialise(&mut builder);
        builder.finish(obj, None);

        let buf = builder.finished_data();
        assert!(!buf.is_empty());

        let xy_data_fb = flatbuffers::root::<fb::XYData>(buf).unwrap();
        let x = xy_data_fb.x().unwrap();
        let y = xy_data_fb.y();

        assert_eq!(x.descriptor().unwrap(), "x");
        assert_eq!(x.value().value_type(), fb::AnyInner::Double);
        assert_eq!(x.value().value_as_double().unwrap().value(), 1.0);

        assert_eq!(y.descriptor().unwrap(), "y");
        assert_eq!(y.value().value_type(), fb::AnyInner::Double);
        assert_eq!(y.value().value_as_double().unwrap().value(), 2.0);
    }
}
