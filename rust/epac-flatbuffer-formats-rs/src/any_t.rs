use crate::pva0_generated as fb;
use crate::serialise::{Serialise, SerialiseCoerce};
use flatbuffers::UnionWIPOffset;
use flatbuffers::WIPOffset;
use numpy::{
    PyArray1, PyArrayDescrMethods, PyArrayMethods, PyReadonlyArray1, PyUntypedArray,
    PyUntypedArrayMethods,
};
use paste::paste;
use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyBool, PyFloat, PyInt, PyString};

/// A dynamic type which can either be a scalar or an array.
///
/// - [`AnyT::Scalar`], containing a single scalar value.
/// - [`AnyT::Array`], containing an array value.
#[derive(FromPyObject)]
pub enum AnyT<'py> {
    Scalar(AnyScalar),
    Array(AnyArray<'py>),
}

/// A dynamic type representing a scalar value.
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

/// A dynamic type representing an array of values.
pub enum AnyArray<'py> {
    BoolArray(PyReadonlyArray1<'py, bool>),
    ByteArray(PyReadonlyArray1<'py, i8>),
    UByteArray(PyReadonlyArray1<'py, u8>),
    ShortArray(PyReadonlyArray1<'py, i16>),
    UShortArray(PyReadonlyArray1<'py, u16>),
    IntArray(PyReadonlyArray1<'py, i32>),
    UIntArray(PyReadonlyArray1<'py, u32>),
    LongArray(PyReadonlyArray1<'py, i64>),
    ULongArray(PyReadonlyArray1<'py, u64>),
    FloatArray(PyReadonlyArray1<'py, f32>),
    DoubleArray(PyReadonlyArray1<'py, f64>),
    StringArray(Vec<String>),
}

/// Declarative macro to serialise variant types into a flatbuffer union.
/// This is used to serialise `AnyScalar` and `AnyArray` variants.
macro_rules! serialise_variant_match {
    ($self:expr, $builder:expr, { $($variant:ident),* $(,)? }) => {
        match $self {
            $(
                Self::$variant(item) => {
                    paste! {
                        let value = item.serialise($builder);
                        let args = fb::[<$variant Args>] {
                            value: value.serialise_coerce(),
                        };
                        let offset = fb::$variant::create($builder, &args);

                        (
                            fb::AnyInner::$variant,
                            offset.as_union_value(),
                        )
                    }
                }
            ),*
        }
    };
}

impl<'py> crate::serialise::Serialise for AnyT<'py> {
    type Output<'out> = flatbuffers::WIPOffset<fb::AnyT<'out>>;
    fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
        let (val_type, inner) = {
            match self {
                AnyT::Scalar(item) => item.serialise_with_discriminant(builder),
                AnyT::Array(item) => item.serialise_with_discriminant(builder),
            }
        };

        let args = fb::AnyTArgs {
            value_type: val_type,
            value: Some(inner),
        };

        fb::AnyT::create(builder, &args)
    }
}

impl AnyScalar {
    fn serialise_with_discriminant(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder,
    ) -> (fb::AnyInner, WIPOffset<UnionWIPOffset>) {
        serialise_variant_match!(self, builder, {
            Bool,
            Double,
            String,
            Long,
            ULong,
            Byte,
            UByte,
            Short,
            UShort,
            Int,
            UInt,
            Float,
        })
    }
}

impl<'py> AnyArray<'py> {
    fn serialise_with_discriminant(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder,
    ) -> (fb::AnyInner, WIPOffset<UnionWIPOffset>) {
        serialise_variant_match!(self, builder, {
            BoolArray,
            ByteArray,
            UByteArray,
            ShortArray,
            UShortArray,
            IntArray,
            UIntArray,
            LongArray,
            ULongArray,
            FloatArray,
            DoubleArray,
            StringArray,
        })
    }
}

/// Implement `FromPyObject` to convert a Python object to `AnyArray<'py>`.
impl<'a, 'py> FromPyObject<'a, 'py> for AnyArray<'py> {
    type Error = PyErr;
    fn extract(obj: Borrowed<'a, 'py, PyAny>) -> Result<Self, Self::Error> {
        let arr = match obj.cast::<PyUntypedArray>() {
            Ok(arr) => arr,
            Err(_) => return Ok(AnyArray::StringArray(obj.extract()?)),
        };
        let dtype = arr.dtype();
        match dtype.char() as char {
            '?' => Ok(AnyArray::BoolArray(
                arr.cast::<PyArray1<bool>>()?.readonly(),
            )),
            'b' => Ok(AnyArray::ByteArray(arr.cast::<PyArray1<i8>>()?.readonly())),
            'B' => Ok(AnyArray::UByteArray(arr.cast::<PyArray1<u8>>()?.readonly())),
            'h' => Ok(AnyArray::ShortArray(
                arr.cast::<PyArray1<i16>>()?.readonly(),
            )),
            'H' => Ok(AnyArray::UShortArray(
                arr.cast::<PyArray1<u16>>()?.readonly(),
            )),
            'i' => Ok(AnyArray::IntArray(arr.cast::<PyArray1<i32>>()?.readonly())),
            'I' => Ok(AnyArray::UIntArray(arr.cast::<PyArray1<u32>>()?.readonly())),
            'l' => match dtype.itemsize() {
                4 => Ok(AnyArray::IntArray(arr.cast::<PyArray1<i32>>()?.readonly())),
                8 => Ok(AnyArray::LongArray(arr.cast::<PyArray1<i64>>()?.readonly())),
                n => Err(PyTypeError::new_err(format!(
                    "unsupported numpy long itemsize {n}"
                ))),
            },
            'L' => match dtype.itemsize() {
                4 => Ok(AnyArray::UIntArray(arr.cast::<PyArray1<u32>>()?.readonly())),
                8 => Ok(AnyArray::ULongArray(
                    arr.cast::<PyArray1<u64>>()?.readonly(),
                )),
                n => Err(PyTypeError::new_err(format!(
                    "unsupported numpy ulong itemsize {n}"
                ))),
            },
            'q' => Ok(AnyArray::LongArray(arr.cast::<PyArray1<i64>>()?.readonly())),
            'Q' => Ok(AnyArray::ULongArray(
                arr.cast::<PyArray1<u64>>()?.readonly(),
            )),
            'f' => Ok(AnyArray::FloatArray(
                arr.cast::<PyArray1<f32>>()?.readonly(),
            )),
            'd' => Ok(AnyArray::DoubleArray(
                arr.cast::<PyArray1<f64>>()?.readonly(),
            )),
            // numpy::Element not implemented for `String`
            'U' => {
                let values: Vec<String> = arr.call_method0("tolist")?.extract()?;
                Ok(AnyArray::StringArray(values))
            }
            _c => Err(PyTypeError::new_err(format!("unknown dtype: char is {_c}"))),
        }
    }
}

/// A type representing a python scalar value.
#[derive(FromPyObject)]
enum PyAnyScalar<'py> {
    Bool(Bound<'py, PyBool>),
    Int(Bound<'py, PyInt>),
    Float(Bound<'py, PyFloat>),
    Str(Bound<'py, PyString>),
}

/// Implement `TryFrom` to convert `PyAnyScalar` to `AnyScalar`.
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

/// Implement `FromPyObject` to convert a Python object to `AnyScalar`.
impl<'a, 'py> FromPyObject<'a, 'py> for AnyScalar {
    type Error = PyErr;
    fn extract(obj: Borrowed<'a, 'py, PyAny>) -> Result<Self, Self::Error> {
        let pyanyarray: PyAnyScalar = obj.extract()?;
        let anyvec = pyanyarray.try_into()?;
        Ok(anyvec)
    }
}
