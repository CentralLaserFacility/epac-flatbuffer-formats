use crate::pva0_generated as fb;
use crate::serialise::{Discriminant, SerialiseCoerce};
use epac_flatbuffers_derive::Serialise;
use flatbuffers::UnionWIPOffset;
use numpy::{
    PyArrayDescrMethods, PyArrayDyn, PyArrayMethods, PyUntypedArray, PyUntypedArrayMethods,
};
use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyBool, PyFloat, PyInt, PyString};

struct AlarmSeverity(u8);
struct AlarmStatus(u8);
struct DisplayForm(u8);

#[derive(FromPyObject)]
pub enum AnyT {
    Scalar(AnyScalar),
    Array(AnyArray),
}

#[allow(unused)]
pub enum AnyScalar {
    Bool(bool),
    Double(f64),
    String(String),
    Long(i64),
    ULong(u64),
    Byte(i8),
    UByte(u8),
    Short(i16),
    UShort(u16),
    Int(i32),
    UInt(u32),
    Float(f32),
}
pub enum AnyArray {
    BoolArray(Vec<bool>),
    ByteArray(Vec<i8>),
    UByteArray(Vec<u8>),
    ShortArray(Vec<i16>),
    UShortArray(Vec<u16>),
    IntArray(Vec<i32>),
    UIntArray(Vec<u32>),
    LongArray(Vec<i64>),
    ULongArray(Vec<u64>),
    FloatArray(Vec<f32>),
    DoubleArray(Vec<f64>),
    StringArray(Vec<String>),
}

macro_rules! serialise_variant {
    ($builder:expr, $item:expr, $variant:ident, $args:ident) => {{
        let value = $item.serialise($builder);
        let args = fb::$args {
            value: value.serialise_coerce(),
        };
        let offset = fb::$variant::create($builder, &args);
        offset.as_union_value()
    }};
}

impl crate::serialise::Serialise for AnyT {
    type Output<'out> = flatbuffers::WIPOffset<fb::AnyT<'out>>;
    fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
        let inner = {
            match self {
                AnyT::Scalar(item) => item.serialise(builder),
                AnyT::Array(item) => item.serialise(builder),
            }
        };
        let val_type = self.discriminant();

        let args = fb::AnyTArgs {
            value_type: val_type.serialise_coerce(),
            value: inner.serialise_coerce(),
        };

        fb::AnyT::create(builder, &args)
    }
}

impl crate::serialise::Discriminant for AnyT {
    type Disc = fb::AnyInner;
    fn discriminant(&self) -> Self::Disc {
        match self {
            AnyT::Scalar(item) => item.discriminant(),
            AnyT::Array(item) => item.discriminant(),
        }
    }
}

impl crate::serialise::Serialise for AnyScalar {
    type Output<'out> = flatbuffers::WIPOffset<UnionWIPOffset>;
    fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
        match self {
            Self::Bool(item) => serialise_variant!(builder, item, Bool, BoolArgs),
            Self::Double(item) => serialise_variant!(builder, item, Double, DoubleArgs),
            Self::String(item) => serialise_variant!(builder, item, String, StringArgs),
            Self::Long(item) => serialise_variant!(builder, item, Long, LongArgs),
            Self::ULong(item) => serialise_variant!(builder, item, ULong, ULongArgs),
            Self::Byte(item) => serialise_variant!(builder, item, Byte, ByteArgs),
            Self::UByte(item) => serialise_variant!(builder, item, UByte, UByteArgs),
            Self::Short(item) => serialise_variant!(builder, item, Short, ShortArgs),
            Self::UShort(item) => serialise_variant!(builder, item, UShort, UShortArgs),
            Self::Int(item) => serialise_variant!(builder, item, Int, IntArgs),
            Self::UInt(item) => serialise_variant!(builder, item, UInt, UIntArgs),
            Self::Float(item) => serialise_variant!(builder, item, Float, FloatArgs),
        }
    }
}

impl crate::serialise::Discriminant for AnyScalar {
    type Disc = fb::AnyInner;
    fn discriminant(&self) -> Self::Disc {
        match self {
            AnyScalar::Bool(_) => fb::AnyInner::Bool,
            AnyScalar::Double(_) => fb::AnyInner::Double,
            AnyScalar::String(_) => fb::AnyInner::String,
            AnyScalar::Long(_) => fb::AnyInner::Long,
            AnyScalar::ULong(_) => fb::AnyInner::ULong,
            AnyScalar::Byte(_) => fb::AnyInner::Byte,
            AnyScalar::UByte(_) => fb::AnyInner::UByte,
            AnyScalar::Short(_) => fb::AnyInner::Short,
            AnyScalar::UShort(_) => fb::AnyInner::UShort,
            AnyScalar::Int(_) => fb::AnyInner::Int,
            AnyScalar::UInt(_) => fb::AnyInner::UInt,
            AnyScalar::Float(_) => fb::AnyInner::Float,
        }
    }
}

impl crate::serialise::Serialise for AnyArray {
    type Output<'out> = flatbuffers::WIPOffset<UnionWIPOffset>;
    fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
        match self {
            Self::BoolArray(item) => serialise_variant!(builder, item, BoolArray, BoolArrayArgs),
            Self::ByteArray(item) => serialise_variant!(builder, item, ByteArray, ByteArrayArgs),
            Self::UByteArray(item) => serialise_variant!(builder, item, UByteArray, UByteArrayArgs),
            Self::ShortArray(item) => serialise_variant!(builder, item, ShortArray, ShortArrayArgs),
            Self::UShortArray(item) => {
                serialise_variant!(builder, item, UShortArray, UShortArrayArgs)
            }
            Self::IntArray(item) => serialise_variant!(builder, item, IntArray, IntArrayArgs),
            Self::UIntArray(item) => serialise_variant!(builder, item, UIntArray, UIntArrayArgs),
            Self::LongArray(item) => serialise_variant!(builder, item, LongArray, LongArrayArgs),
            Self::ULongArray(item) => serialise_variant!(builder, item, ULongArray, ULongArrayArgs),
            Self::FloatArray(item) => serialise_variant!(builder, item, FloatArray, FloatArrayArgs),
            Self::DoubleArray(item) => {
                serialise_variant!(builder, item, DoubleArray, DoubleArrayArgs)
            }
            Self::StringArray(item) => {
                serialise_variant!(builder, item, StringArray, StringArrayArgs)
            }
        }
    }
}

impl crate::serialise::Discriminant for AnyArray {
    type Disc = fb::AnyInner;
    fn discriminant(&self) -> Self::Disc {
        match self {
            AnyArray::BoolArray(_) => fb::AnyInner::BoolArray,
            AnyArray::ByteArray(_) => fb::AnyInner::ByteArray,
            AnyArray::UByteArray(_) => fb::AnyInner::UByteArray,
            AnyArray::ShortArray(_) => fb::AnyInner::ShortArray,
            AnyArray::UShortArray(_) => fb::AnyInner::UShortArray,
            AnyArray::IntArray(_) => fb::AnyInner::IntArray,
            AnyArray::UIntArray(_) => fb::AnyInner::UIntArray,
            AnyArray::LongArray(_) => fb::AnyInner::LongArray,
            AnyArray::ULongArray(_) => fb::AnyInner::ULongArray,
            AnyArray::FloatArray(_) => fb::AnyInner::FloatArray,
            AnyArray::DoubleArray(_) => fb::AnyInner::DoubleArray,
            AnyArray::StringArray(_) => fb::AnyInner::StringArray,
        }
    }
}

/// This is used as an intermediate to enable proper
/// strongly-typed conversions from numpy array to Vec<T>
/// The problem is that PyO3 tries to hard to convert
/// "any iterable of things that can be converted to type T"
/// to `Vec<T>`, so in particular the types of integers can be lost.
#[derive(FromPyObject)]
enum PyAnyArray<'py> {
    Numeric(Bound<'py, PyUntypedArray>),
    Str(Vec<String>),
}

impl TryFrom<PyAnyArray<'_>> for AnyArray {
    type Error = PyErr;
    fn try_from(value: PyAnyArray<'_>) -> Result<Self, Self::Error> {
        let v = match value {
            PyAnyArray::Numeric(arr) => {
                let dtype = arr.dtype();
                match dtype.char() as char {
                    '?' => AnyArray::BoolArray(arr.cast::<PyArrayDyn<bool>>()?.to_vec()?),
                    'b' => AnyArray::ByteArray(arr.cast::<PyArrayDyn<i8>>()?.to_vec()?),
                    'B' => AnyArray::UByteArray(arr.cast::<PyArrayDyn<u8>>()?.to_vec()?),
                    'h' => AnyArray::ShortArray(arr.cast::<PyArrayDyn<i16>>()?.to_vec()?),
                    'H' => AnyArray::UShortArray(arr.cast::<PyArrayDyn<u16>>()?.to_vec()?),
                    'i' => AnyArray::IntArray(arr.cast::<PyArrayDyn<i32>>()?.to_vec()?),
                    'I' => AnyArray::UIntArray(arr.cast::<PyArrayDyn<u32>>()?.to_vec()?),
                    'l' => match dtype.itemsize() {
                        4 => AnyArray::IntArray(arr.cast::<PyArrayDyn<i32>>()?.to_vec()?),
                        8 => AnyArray::LongArray(arr.cast::<PyArrayDyn<i64>>()?.to_vec()?),
                        n => {
                            return Err(PyTypeError::new_err(format!(
                                "unsupported numpy long itemsize {n}"
                            )))
                        }
                    },
                    'L' => match dtype.itemsize() {
                        4 => AnyArray::UIntArray(arr.cast::<PyArrayDyn<u32>>()?.to_vec()?),
                        8 => AnyArray::ULongArray(arr.cast::<PyArrayDyn<u64>>()?.to_vec()?),
                        n => {
                            return Err(PyTypeError::new_err(format!(
                                "unsupported numpy ulong itemsize {n}"
                            )))
                        }
                    },
                    'q' => AnyArray::LongArray(arr.cast::<PyArrayDyn<i64>>()?.to_vec()?),
                    'Q' => AnyArray::ULongArray(arr.cast::<PyArrayDyn<u64>>()?.to_vec()?),
                    'f' => AnyArray::FloatArray(arr.cast::<PyArrayDyn<f32>>()?.to_vec()?),
                    'd' => AnyArray::DoubleArray(arr.cast::<PyArrayDyn<f64>>()?.to_vec()?),
                    'U' => {
                        let values: Vec<String> = arr.call_method0("tolist")?.extract()?;
                        AnyArray::StringArray(values)
                    }
                    _c => return Err(PyTypeError::new_err(format!("unknown dtype: char is {_c}"))),
                }
            }
            PyAnyArray::Str(s) => AnyArray::StringArray(s),
        };
        Ok(v)
    }
}

impl<'a, 'py> FromPyObject<'a, 'py> for AnyArray {
    type Error = PyErr;
    fn extract(obj: Borrowed<'a, 'py, PyAny>) -> Result<Self, Self::Error> {
        let pyanyarray: PyAnyArray = obj.extract()?;
        let anyvec = pyanyarray.try_into()?;
        Ok(anyvec)
    }
}

#[derive(FromPyObject)]
enum PyAnyScalar<'py> {
    Bool(Bound<'py, PyBool>),
    Int(Bound<'py, PyInt>),
    Float(Bound<'py, PyFloat>),
    Str(Bound<'py, PyString>),
}
impl TryFrom<PyAnyScalar<'_>> for AnyScalar {
    type Error = PyErr;
    fn try_from(value: PyAnyScalar<'_>) -> Result<Self, Self::Error> {
        Ok(match value {
            PyAnyScalar::Bool(b) => AnyScalar::Bool(b.is_true()),
            PyAnyScalar::Int(i) => {
                if let Ok(signed) = i.extract::<i64>() {
                    AnyScalar::Long(signed)
                } else {
                    let unsigned = i.extract::<u64>()?;
                    AnyScalar::ULong(unsigned)
                }
            }
            PyAnyScalar::Float(f) => AnyScalar::Double(f.value()),
            PyAnyScalar::Str(s) => AnyScalar::String(s.to_string()),
        })
    }
}

impl<'a, 'py> FromPyObject<'a, 'py> for AnyScalar {
    type Error = PyErr;
    fn extract(obj: Borrowed<'a, 'py, PyAny>) -> Result<Self, Self::Error> {
        let pyanyarray: PyAnyScalar = obj.extract()?;
        let anyvec = pyanyarray.try_into()?;
        Ok(anyvec)
    }
}

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

// declarative macro to get u8 wrapper from py object
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

#[derive(Serialise, FromPyObject)]
struct AlarmT {
    severity: AlarmSeverity,
    status: AlarmStatus,
    message: Option<String>,
}

#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
struct TimeT {
    seconds_past_epoch: i64,
    nanoseconds: i32,
    user_tag: i32,
}

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

#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
struct ControlT {
    limit_low: f64,
    limit_high: f64,
    min_step: f64,
}

#[derive(Serialise, FromPyObject)]
struct CodecT {
    name: String,
}

#[derive(Serialise, FromPyObject)]
struct Column {
    value: AnyT,
}

#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
struct DimensionT {
    size_: i32,
    offset: i32,
    full_size: i32,
    binning: i32,
    reverse: bool,
}

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

#[derive(Serialise, FromPyObject)]
pub struct XYData {
    x: NTScalarAny,
    y: NTScalarAny,
}

#[derive(Serialise, FromPyObject)]
struct PulseID {
    value: u64,
    #[pyo3(attribute("timestamp"))]
    time_stamp: f64,
}

enum PVType {
    Scalar(NTScalarAny),
    NdArray(NTNDArray),
    Table(NTTable),
    XY(XYData),
}

impl<'py> FromPyObject<'_, 'py> for PVType {
    type Error = PyErr;
    fn extract(obj: pyo3::Borrowed<'_, 'py, PyAny>) -> PyResult<Self> {
        if let Ok(v) = obj.extract::<NTScalarAny>() {
            return Ok(PVType::Scalar(v));
        }

        if let Ok(v) = obj.extract::<NTNDArray>() {
            return Ok(PVType::NdArray(v));
        }

        if let Ok(v) = obj.extract::<NTTable>() {
            return Ok(PVType::Table(v));
        }

        if let Ok(v) = obj.extract::<XYData>() {
            return Ok(PVType::XY(v));
        }

        Err(pyo3::exceptions::PyTypeError::new_err(
            "unable to convert object into Data",
        ))
    }
}

impl crate::serialise::Serialise for PVType {
    type Output<'out> = flatbuffers::WIPOffset<UnionWIPOffset>;
    fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
        match self {
            PVType::Scalar(val) => val.serialise(builder).as_union_value(),
            PVType::NdArray(val) => val.serialise(builder).as_union_value(),
            PVType::Table(val) => val.serialise(builder).as_union_value(),
            PVType::XY(val) => val.serialise(builder).as_union_value(),
        }
    }
}

impl crate::serialise::Discriminant for PVType {
    type Disc = fb::PVType;
    fn discriminant(&self) -> Self::Disc {
        match self {
            PVType::Scalar(_) => fb::PVType::NTScalarAny,
            PVType::NdArray(_) => fb::PVType::NTNDArray,
            PVType::Table(_) => fb::PVType::NTTable,
            PVType::XY(_) => fb::PVType::XYData,
        }
    }
}

#[derive(Serialise, FromPyObject)]
#[pyo3(rename_all = "camelCase")]
pub struct PVData {
    #[serialise(variant)]
    data: PVType,
    source_name: String,
    pulse_id: Option<PulseID>,
}
