use crate::pva0_generated as fb;
use crate::serialise::{Serialise, SerialiseCoerce};
use flatbuffers::UnionWIPOffset;
use flatbuffers::WIPOffset;
use numpy::{
    PyArrayDescrMethods, PyArrayDyn, PyArrayMethods, PyUntypedArray, PyUntypedArrayMethods,
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
pub enum AnyT {
    Scalar(AnyScalar),
    Array(AnyArray),
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

impl crate::serialise::Serialise for AnyT {
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

impl AnyArray {
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

/// A type representing a python array.
///
/// An intermediate to enable proper strongly-typed conversions
/// from numpy array to Vec<T>.
///
/// The problem is that PyO3 tries to hard to convert
/// "any iterable of things that can be converted to type T"
/// to `Vec<T>`, so in particular the types of integers can be lost.
#[derive(FromPyObject)]
enum PyAnyArray<'py> {
    Numeric(Bound<'py, PyUntypedArray>),
    Str(Vec<String>),
}

/// Implement `TryFrom` to convert `PyAnyArray` to `AnyArray`.
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

/// Implement `FromPyObject` to convert a Python object to `AnyArray`.
impl<'a, 'py> FromPyObject<'a, 'py> for AnyArray {
    type Error = PyErr;
    fn extract(obj: Borrowed<'a, 'py, PyAny>) -> Result<Self, Self::Error> {
        let pyanyarray: PyAnyArray = obj.extract()?;
        let anyvec = pyanyarray.try_into()?;
        Ok(anyvec)
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
