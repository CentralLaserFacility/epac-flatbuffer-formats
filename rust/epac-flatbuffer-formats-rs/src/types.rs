use pyo3::types::PyAnyMethods;

#[derive(pyo3::FromPyObject)]
pub struct TimeT {
    #[pyo3(attribute("secondsPastEpoch"))]
    pub seconds_past_epoch: i64,
    pub nanoseconds: i32,
    #[pyo3(attribute("userTag"))]
    pub user_tag: i32,
}

impl TimeT {
    pub fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<crate::pva0::TimeT<'a>> {
        crate::pva0::TimeT::create(
            builder,
            &crate::pva0::TimeTArgs {
                seconds_past_epoch: self.seconds_past_epoch,
                nanoseconds: self.nanoseconds,
                user_tag: self.user_tag,
            },
        )
    }
}

#[derive(pyo3::FromPyObject)]
pub struct AlarmT {
    pub severity: u8,
    pub status: u8,
    pub message: String,
}

impl AlarmT {
    pub fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<crate::pva0::AlarmT<'a>> {
        let message = builder.create_string(&self.message);
        crate::pva0::AlarmT::create(
            builder,
            &crate::pva0::AlarmTArgs {
                severity: crate::pva0::AlarmSeverity(self.severity),
                status: crate::pva0::AlarmStatus(self.status),
                message: Some(message),
            },
        )
    }
}

#[derive(pyo3::FromPyObject)]
pub struct ControlT {
    #[pyo3(attribute("limitLow"))]
    pub limit_low: f64,
    #[pyo3(attribute("limitHigh"))]
    pub limit_high: f64,
    #[pyo3(attribute("minStep"))]
    pub min_step: f64,
}

impl ControlT {
    pub fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<crate::pva0::ControlT<'a>> {
        crate::pva0::ControlT::create(
            builder,
            &crate::pva0::ControlTArgs {
                limit_low: self.limit_low,
                limit_high: self.limit_high,
                min_step: self.min_step,
            },
        )
    }
}


#[derive(pyo3::FromPyObject)]
pub struct DisplayT {
    #[pyo3(attribute("limitLow"))]
    pub limit_low: f64,
    #[pyo3(attribute("limitHigh"))]
    pub limit_high: f64,
    pub description: String,
    pub units: String,
    pub precision: i32,
    pub form: u8,
}

impl DisplayT {
    pub fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<crate::pva0::DisplayT<'a>> {
        let description = builder.create_string(&self.description);
        let units = builder.create_string(&self.units);

        crate::pva0::DisplayT::create(
            builder,
            &crate::pva0::DisplayTArgs {
                limit_low: self.limit_low,
                limit_high: self.limit_high,
                description: Some(description),
                units: Some(units),
                precision: self.precision,
                form: crate::pva0::DisplayForm(self.form),
            },
        )
    }
}



// pub enum AnyScalar {
//     Double(f64),
// }

// impl AnyScalar {
//     pub fn serialise<'a>(
//         &self,
//         builder: &mut flatbuffers::FlatBufferBuilder<'a>,
//     ) -> flatbuffers::WIPOffset<crate::pva0::AnyT<'a>> {
//         match self {
//             AnyScalar::Double(v) => {
//                 let inner = crate::pva0::Double::create(
//                     builder,
//                     &crate::pva0::DoubleArgs { value: *v },
//                 );
//                 crate::pva0::AnyT::create(
//                     builder,
//                     &crate::pva0::AnyTArgs {
//                         value_type: crate::pva0::AnyInner::Double,
//                         value: Some(inner.as_union_value()),
//                     },
//                 )
//             }
//         }
//     }
// }



pub enum AnyScalar {
    Bool(bool),
    Byte(i8),
    UByte(u8),
    Short(i16),
    UShort(u16),
    Int(i32),
    UInt(u32),
    Long(i64),
    ULong(u64),
    Float(f32),
    Double(f64),
    String(String),
}

// impl pyo3::FromPyObject<'_, '_> for AnyScalar {
//     type Error = pyo3::PyErr;

//     fn extract(obj: pyo3::Borrowed<'_, '_, pyo3::PyAny>) -> Result<Self, Self::Error> {
//         let dtype_name: String = obj
//             .getattr("dtype")?
//             .getattr("name")?
//             .extract()?;

//         match dtype_name.as_str() {
//             "bool" => Ok(AnyScalar::Bool(obj.extract()?)),
//             "int32" => Ok(AnyScalar::Int(obj.extract()?)),
//             "int64" => Ok(AnyScalar::Long(obj.extract()?)),
//             "float32" => Ok(AnyScalar::Float(obj.extract()?)),
//             "float64" => Ok(AnyScalar::Double(obj.extract()?)),
//             other => Err(pyo3::exceptions::PyTypeError::new_err(format!(
//                 "unsupported scalar dtype: {other}"
//             ))),
//         }
//     }
// }


impl pyo3::FromPyObject<'_, '_> for AnyScalar {
    type Error = pyo3::PyErr;

    fn extract(obj: pyo3::Borrowed<'_, '_, pyo3::PyAny>) -> Result<Self, Self::Error> {
        let dtype = obj.getattr("dtype")?;
        let kind: String = dtype.getattr("kind")?.extract()?;

        if kind == "U" {
            return Ok(AnyScalar::String(obj.extract()?));
        }

        let name: String = dtype.getattr("name")?.extract()?;
        match name.as_str() {
            "bool" => Ok(AnyScalar::Bool(obj.extract()?)),
            "byte" | "int8" => Ok(AnyScalar::Byte(obj.extract()?)),
            "ubyte" | "uint8" => Ok(AnyScalar::UByte(obj.extract()?)),
            "int16" => Ok(AnyScalar::Short(obj.extract()?)),
            "uint16" => Ok(AnyScalar::UShort(obj.extract()?)),
            "int32" => Ok(AnyScalar::Int(obj.extract()?)),
            "uint32" => Ok(AnyScalar::UInt(obj.extract()?)),
            "int64" => Ok(AnyScalar::Long(obj.extract()?)),
            "uint64" => Ok(AnyScalar::ULong(obj.extract()?)),
            "float32" => Ok(AnyScalar::Float(obj.extract()?)),
            "float64" => Ok(AnyScalar::Double(obj.extract()?)),
            other => Err(pyo3::exceptions::PyTypeError::new_err(format!(
                "unsupported scalar dtype: {other}"
            ))),
        }
    }
}

impl AnyScalar {
    pub fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<crate::pva0::AnyT<'a>> {
        match self {
            AnyScalar::Bool(v) => {
                let inner = crate::pva0::Bool::create(builder, &crate::pva0::BoolArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::Bool,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::Byte(v) => {
                let inner = crate::pva0::Byte::create(builder, &crate::pva0::ByteArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::Byte,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::UByte(v) => {
                let inner = crate::pva0::UByte::create(builder, &crate::pva0::UByteArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::UByte,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::Short(v) => {
                let inner = crate::pva0::Short::create(builder, &crate::pva0::ShortArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::Short,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::UShort(v) => {
                let inner = crate::pva0::UShort::create(builder, &crate::pva0::UShortArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::UShort,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::Int(v) => {
                let inner = crate::pva0::Int::create(builder, &crate::pva0::IntArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::Int,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::UInt(v) => {
                let inner = crate::pva0::UInt::create(builder, &crate::pva0::UIntArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::UInt,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::Long(v) => {
                let inner = crate::pva0::Long::create(builder, &crate::pva0::LongArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::Long,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::ULong(v) => {
                let inner = crate::pva0::ULong::create(builder, &crate::pva0::ULongArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::ULong,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::Float(v) => {
                let inner = crate::pva0::Float::create(builder, &crate::pva0::FloatArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::Float,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::Double(v) => {
                let inner = crate::pva0::Double::create(builder, &crate::pva0::DoubleArgs { value: *v });
                crate::pva0::AnyT::create(
                    builder,
                    &crate::pva0::AnyTArgs {
                        value_type: crate::pva0::AnyInner::Double,
                        value: Some(inner.as_union_value()),
                    },
                )
            }
            AnyScalar::String(v) => {
                let string_offset = builder.create_string(v);
                let inner = crate::pva0::String::create(builder, &crate::pva0::StringArgs { value: Some(string_offset) });
                crate::pva0::AnyT::create(builder, &crate::pva0::AnyTArgs {
                    value_type: crate::pva0::AnyInner::String,
                    value: Some(inner.as_union_value()),
                })
            }
        }
    }
}

// pub struct IntArrayT {
//     pub value: Vec<i32>,
// }

// impl pyo3::FromPyObject<'_, '_> for IntArrayT {
//     type Error = pyo3::PyErr;

//     fn extract(obj: pyo3::Borrowed<'_, '_, pyo3::PyAny>) -> Result<Self, Self::Error> {
//         let arr: numpy::PyReadonlyArray1<i32> = obj.extract()?;
//         Ok(IntArrayT {
//             value: arr.as_slice()?.to_vec(),
//         })
//     }
// }

// impl IntArrayT {
//     pub fn serialise<'a>(
//         &self,
//         builder: &mut flatbuffers::FlatBufferBuilder<'a>,
//     ) -> flatbuffers::WIPOffset<crate::pva0::IntArray<'a>> {
//         let vector = builder.create_vector(&self.value);
//         crate::pva0::IntArray::create(
//             builder,
//             &crate::pva0::IntArrayArgs {
//                 value: Some(vector),
//             },
//         )
//     }
// }


pub enum AnyArray {
    Bool(Vec<bool>),
    Byte(Vec<i8>),
    UByte(Vec<u8>),
    Short(Vec<i16>),
    UShort(Vec<u16>),
    Int(Vec<i32>),
    UInt(Vec<u32>),
    Long(Vec<i64>),
    ULong(Vec<u64>),
    Float(Vec<f32>),
    Double(Vec<f64>),
}

impl<'a, 'py> pyo3::FromPyObject<'a, 'py> for AnyArray {
    type Error = pyo3::PyErr;

    fn extract(obj: pyo3::Borrowed<'a, 'py, pyo3::PyAny>) -> Result<Self, Self::Error> {
        use numpy::{PyArrayDescrMethods, PyArrayMethods, PyUntypedArrayMethods};

        let arr: pyo3::Bound<'py, numpy::PyUntypedArray> = obj.extract()?;
        let kind = arr.dtype().kind();
        let itemsize = arr.dtype().itemsize();

        Ok(match (kind, itemsize) {
            (b'b', 1) => AnyArray::Bool(arr.cast::<numpy::PyArray1<bool>>()?.to_vec()?),
            (b'i', 1) => AnyArray::Byte(arr.cast::<numpy::PyArray1<i8>>()?.to_vec()?),
            (b'u', 1) => AnyArray::UByte(arr.cast::<numpy::PyArray1<u8>>()?.to_vec()?),
            (b'i', 2) => AnyArray::Short(arr.cast::<numpy::PyArray1<i16>>()?.to_vec()?),
            (b'u', 2) => AnyArray::UShort(arr.cast::<numpy::PyArray1<u16>>()?.to_vec()?),
            (b'i', 4) => AnyArray::Int(arr.cast::<numpy::PyArray1<i32>>()?.to_vec()?),
            (b'u', 4) => AnyArray::UInt(arr.cast::<numpy::PyArray1<u32>>()?.to_vec()?),
            (b'i', 8) => AnyArray::Long(arr.cast::<numpy::PyArray1<i64>>()?.to_vec()?),
            (b'u', 8) => AnyArray::ULong(arr.cast::<numpy::PyArray1<u64>>()?.to_vec()?),
            (b'f', 4) => AnyArray::Float(arr.cast::<numpy::PyArray1<f32>>()?.to_vec()?),
            (b'f', 8) => AnyArray::Double(arr.cast::<numpy::PyArray1<f64>>()?.to_vec()?),
            (k, s) => {
                return Err(pyo3::exceptions::PyTypeError::new_err(format!(
                    "unsupported array dtype: kind={k}, itemsize={s}"
                )));
            }
        })
    }
}

impl AnyArray {
    pub fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<crate::pva0::AnyT<'a>> {
        match self {
            AnyArray::Bool(v) => {
                let vector = builder.create_vector(v);
                let inner = crate::pva0::BoolArray::create(
                    builder,
                    &crate::pva0::BoolArrayArgs { value: Some(vector) },
                );
                crate::pva0::AnyT::create(builder, &crate::pva0::AnyTArgs {
                    value_type: crate::pva0::AnyInner::BoolArray,
                    value: Some(inner.as_union_value()),
                })
            }
            AnyArray::Int(v) => {
                let vector = builder.create_vector(v);
                let inner = crate::pva0::IntArray::create(
                    builder,
                    &crate::pva0::IntArrayArgs { value: Some(vector) },
                );
                crate::pva0::AnyT::create(builder, &crate::pva0::AnyTArgs {
                    value_type: crate::pva0::AnyInner::IntArray,
                    value: Some(inner.as_union_value()),
                })
            }
            // Byte, UByte, Short, UShort, UInt, Long, ULong, Float, Double —
            // identical shape, swap type names (same exercise as AnyScalar)
            _ => todo!(),
        }
    }
}


#[derive(pyo3::FromPyObject)]
pub struct NTScalarAny {
    pub value: AnyScalar,
    pub descriptor: String,
    pub alarm: AlarmT,
    #[pyo3(attribute("timeStamp"))]
    pub time_stamp: TimeT,
    pub display: DisplayT,
    pub control: ControlT,
}


impl NTScalarAny {
    pub fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<crate::pva0::NTScalarAny<'a>> {
        let descriptor = builder.create_string(&self.descriptor);
        // let value = AnyScalar::Double(self.value).serialise(builder);
        let value = self.value.serialise(builder);
        let alarm = self.alarm.serialise(builder);
        let time_stamp = self.time_stamp.serialise(builder);
        let display = self.display.serialise(builder);
        let control = self.control.serialise(builder);

        crate::pva0::NTScalarAny::create(
            builder,
            &crate::pva0::NTScalarAnyArgs {
                value: Some(value),
                descriptor: Some(descriptor),
                alarm: Some(alarm),
                time_stamp: Some(time_stamp),
                display: Some(display),
                control: Some(control),
            },
        )
    }
}