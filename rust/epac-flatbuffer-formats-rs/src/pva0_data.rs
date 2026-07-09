use crate::pva0_generated;
use numpy::{PyArray1, PyArray2};
use pyo3::prelude::*;

trait SerialiseAny {
    fn serialise_any<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::AnyT<'a>>;
}

impl<T> SerialiseAny for Option<T>
where
    T: SerialiseAny,
{
    fn serialise_any<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::AnyT<'a>> {
        match self {
            Some(value) => value.serialise_any(builder),
            None => pva0_generated::AnyT::create(
                builder,
                &pva0_generated::AnyTArgs {
                    value: None,
                    value_type: pva0_generated::AnyInner::NONE,
                },
            ),
        }
    }
}

impl SerialiseAny for [u8] {
    fn serialise_any<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::AnyT<'a>> {
        let value = builder.create_vector(self);
        let value = pva0_generated::UByteArray::create(
            builder,
            &pva0_generated::UByteArrayArgs { value: Some(value) },
        );
        pva0_generated::AnyT::create(
            builder,
            &pva0_generated::AnyTArgs {
                value: Some(value.as_union_value()),
                value_type: pva0_generated::AnyInner::UByteArray,
            },
        )
    }
}

impl SerialiseAny for str {
    fn serialise_any<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::AnyT<'a>> {
        let value = builder.create_string(self);
        let value = pva0_generated::String::create(
            builder,
            &pva0_generated::StringArgs { value: Some(value) },
        );
        pva0_generated::AnyT::create(
            builder,
            &pva0_generated::AnyTArgs {
                value: Some(value.as_union_value()),
                value_type: pva0_generated::AnyInner::String,
            },
        )
    }
}

impl SerialiseAny for String {
    fn serialise_any<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::AnyT<'a>> {
        self.as_str().serialise_any(builder)
    }
}

impl SerialiseAny for f64 {
    fn serialise_any<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::AnyT<'a>> {
        let value =
            pva0_generated::Double::create(builder, &pva0_generated::DoubleArgs { value: *self });
        pva0_generated::AnyT::create(
            builder,
            &pva0_generated::AnyTArgs {
                value: Some(value.as_union_value()),
                value_type: pva0_generated::AnyInner::Double,
            },
        )
    }
}

impl SerialiseAny for i64 {
    fn serialise_any<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::AnyT<'a>> {
        let value =
            pva0_generated::Long::create(builder, &pva0_generated::LongArgs { value: *self });
        pva0_generated::AnyT::create(
            builder,
            &pva0_generated::AnyTArgs {
                value: Some(value.as_union_value()),
                value_type: pva0_generated::AnyInner::Long,
            },
        )
    }
}

impl SerialiseAny for bool {
    fn serialise_any<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::AnyT<'a>> {
        let value =
            pva0_generated::Bool::create(builder, &pva0_generated::BoolArgs { value: *self });
        pva0_generated::AnyT::create(
            builder,
            &pva0_generated::AnyTArgs {
                value: Some(value.as_union_value()),
                value_type: pva0_generated::AnyInner::Bool,
            },
        )
    }
}

#[allow(unused)]
enum AnyScalar {
    Bool(bool),
    // Byte(i8),
    // UByte(u8),
    // Short(i16),
    // UShort(u16),
    // Int(i32),
    // UInt(u32),
    Long(i64),
    ULong(u64),
    // Float(f32),
    Double(f64),
    String(String),
}

#[allow(unused)]
enum AnyArray<T> {
    PyArray1(PyArray1<T>),
    PyArray2(PyArray2<T>),
}


#[derive(FromPyObject)]
struct AlarmT {
    severity: u8,
    status: u8,
    message: Option<String>,
}

impl AlarmT {
    // this generates the flatbuffer's offset... better name?
    fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::AlarmT<'a>> {
        let svty = pva0_generated::AlarmSeverity(self.severity);
        let sts = pva0_generated::AlarmStatus(self.status);
        let msg = builder.create_string(self.message.as_ref().unwrap());
        pva0_generated::AlarmT::create(
            builder,
            &pva0_generated::AlarmTArgs {
                severity: svty,
                status: sts,
                message: Some(msg),
            },
        )
    }
}

#[derive(FromPyObject)]
#[pyo3(rename_all = "camelCase")]
struct TimeT {
    seconds_past_epoch: i64,
    nanoseconds: i32,
    user_tag: i32,
}

impl TimeT {
    fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::TimeT<'a>> {
        pva0_generated::TimeT::create(
            builder,
            &pva0_generated::TimeTArgs {
                seconds_past_epoch: self.seconds_past_epoch,
                nanoseconds: self.nanoseconds,
                user_tag: self.user_tag,
            },
        )
    }
}

#[derive(FromPyObject)]
#[pyo3(rename_all = "camelCase")]
#[allow(unused)]
struct DisplayT {
    limit_low: f64,
    limit_high: f64,
    description: String,
    units: String,
    precision: i32,
    form: u8,
}

#[allow(unused)]
impl DisplayT {
    fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::DisplayT<'a>> {
        let desc = builder.create_string(&self.description);
        let unit = builder.create_string(&self.units);
        let display_form = pva0_generated::DisplayForm(self.form);
        pva0_generated::DisplayT::create(
            builder,
            &pva0_generated::DisplayTArgs {
                limit_low: self.limit_low,
                limit_high: self.limit_high,
                description: Some(desc),
                units: Some(unit),
                precision: self.precision,
                form: display_form,
            },
        )
    }
}

#[allow(unused)]
#[derive(FromPyObject)]
#[pyo3(rename_all = "camelCase")]
struct ControlT {
    limit_low: f64,
    limit_high: f64,
    min_step: f64,
}

#[allow(unused)]
impl ControlT {
    fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::ControlT<'a>> {
        pva0_generated::ControlT::create(
            builder,
            &pva0_generated::ControlTArgs {
                limit_low: self.limit_low,
                limit_high: self.limit_high,
                min_step: self.min_step,
            },
        )
    }
}
#[derive(FromPyObject)]
#[pyo3(rename_all = "camelCase")]
pub struct NTScalarAny {
    // AnyScalar work been done by anuj
    value: f64,
    descriptor: String,
    alarm: Option<AlarmT>,
    time_stamp: Option<TimeT>,
    display: Option<DisplayT>,
    control: Option<ControlT>,
}

#[allow(unused)]
impl NTScalarAny {
    pub fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::NTScalarAny<'a>> {
        let value = self.value.serialise_any(builder);
        let desc = builder.create_string(&self.descriptor);
        let alarm = self.alarm.as_ref().map(|alarm| alarm.serialise(builder));
        let ts = self.time_stamp.as_ref().map(|ts| ts.serialise(builder));
        let display = self
            .display
            .as_ref()
            .map(|display| display.serialise(builder));
        let ctrl = self
            .control
            .as_ref()
            .map(|control| control.serialise(builder));
        pva0_generated::NTScalarAny::create(
            builder,
            &pva0_generated::NTScalarAnyArgs {
                value: Some(value),
                descriptor: Some(desc),
                alarm,
                time_stamp: ts,
                display,
                control: ctrl,
            },
        )
    }
}

#[allow(unused)]
#[derive(FromPyObject)]
#[pyo3(rename_all = "camelCase")]
pub struct PVData {
    data: NTScalarAny,
    source_name: String,
}

#[allow(unused)]
impl PVData {
    pub fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<pva0_generated::PVData<'a>> {
        let data = self.data.serialise(builder);
        let source_name = builder.create_string(&self.source_name);
        pva0_generated::PVData::create(
            builder,
            &pva0_generated::PVDataArgs {
                data_type: pva0_generated::PVType::NTScalarAny,
                data: Some(data.as_union_value()),
                source_name: Some(source_name),
                pulse_id: None,
            },
        )
    }
}
