use flatbuffers::{Push, WIPOffset};

#[diagnostic::on_unimplemented(message = "{Self} cannot be converted to {T} during serialisation")]
pub trait SerialiseCoerce<T> {
    fn serialise_coerce(self) -> T;
}

impl<T> SerialiseCoerce<T> for T {
    fn serialise_coerce(self) -> T {
        self
    }
}

impl<T> SerialiseCoerce<Option<T>> for T {
    fn serialise_coerce(self) -> Option<T> {
        Some(self)
    }
}

pub trait Serialise {
    type Output<'out>;
    fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a>;

    // Default impl uses a map+collect over Self::serialise. Types that do not need to be serialised
    // (primitives that are themselves `Push`) should reimplement this to elide the map and collect.
    fn serialise_slice<'a>(
        items: &[Self],
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> WIPOffset<flatbuffers::Vector<'a, <Self::Output<'a> as Push>::Output>>
    where
        Self: Sized,
        for<'out> Self::Output<'out>: Push,
    {
        let items = items
            .iter()
            .map(|each| each.serialise(builder))
            .collect::<Vec<_>>();
        builder.create_vector(&items)
    }
}

pub trait Discriminant {
    type Disc;

    fn discriminant(&self) -> Self::Disc;
}

// impl<U: Serialise + ?Sized, T: Deref<Target = U>> Serialise for Option<T> {
//     type Output<'a> = Option<U::Output<'a>>;
//     fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
//         self.as_deref().map(|x| x.serialise(builder))
//     }
// }

impl<T: Serialise> Serialise for Option<T> {
    type Output<'a> = Option<T::Output<'a>>;
    fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
        self.as_ref().map(|x| x.serialise(builder))
    }
}

impl<T: 'static + Serialise> Serialise for [T]
where
    for<'a> T::Output<'a>: flatbuffers::Push,
{
    type Output<'a> = flatbuffers::WIPOffset<
        flatbuffers::Vector<'a, <T::Output<'a> as flatbuffers::Push>::Output>,
    >;
    fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
        T::serialise_slice(self, builder)
    }
}

macro_rules! serialise_primitives {
    ($($prim:ty)*) => {
        $(
        impl Serialise for $prim {
            type Output<'a> = Self;

            fn serialise<'a>(&self, _builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self {
                *self
            }

            fn serialise_slice<'a>(
                items: &[Self],
                builder: &mut flatbuffers::FlatBufferBuilder<'a>,
            ) -> WIPOffset<flatbuffers::Vector<'a, <Self::Output<'a> as Push>::Output>>
            {
                builder.create_vector(items)
            }
        }
    )*
    };
}

serialise_primitives!(bool u8 u16 u32 u64 i8 i16 i32 i64 f32 f64);

impl Serialise for str {
    type Output<'a> = flatbuffers::WIPOffset<&'a str>;

    fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<&'a str> {
        builder.create_string(self)
    }
}

impl Serialise for String {
    type Output<'a> = flatbuffers::WIPOffset<&'a str>;

    fn serialise<'a>(
        &self,
        builder: &mut flatbuffers::FlatBufferBuilder<'a>,
    ) -> flatbuffers::WIPOffset<&'a str> {
        builder.create_string(self)
    }
}

// add implementation for tuple struct
