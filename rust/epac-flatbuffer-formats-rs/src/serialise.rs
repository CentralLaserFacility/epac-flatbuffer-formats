//! This module defines the `Serialise`, `serialise_coerce` and `discriminant` traits,
//! which are used to serialise rust data structures ito flatbuffers.
//!
//! It also implements these traits for the primitive types, as well as for `Option<T>` and `[T]` where `T` implements `Serialise`.
//!

use flatbuffers::{Push, WIPOffset};
use numpy::{Element, PyReadonlyArray1};

/// This trait exists to bridge differences between the Rust representation and
/// the FlatBuffers schema during serialisation. In practice, the Rust side may hold a
/// plain value T, while the FlatBuffers schema expects Option<T> for an optional field.
///
/// SerialiseCoerce allows the serializer to convert the value when the schema requires
/// the optional form.
///
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

/// This trait defines the `serialise` method which is used
/// to serilise rust data stuctures into the flatbuffer format.
///
pub trait Serialise {
    type Output<'out>: 'out;
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

/// This trait is used for FlatBuffers union-like values represented in Rust as enum types.
///
/// The discriminant method returns the active union variant so the serializer can write the
/// correct type tag before serialising the payload.
///
pub trait Discriminant {
    type Disc;

    fn discriminant(&self) -> Self::Disc;
}

impl<T: Serialise> Serialise for Option<T> {
    type Output<'a> = Option<T::Output<'a>>;
    fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
        self.as_ref().map(|x| x.serialise(builder))
    }
}

impl<T: Serialise> Serialise for [T]
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

impl<T> Serialise for PyReadonlyArray1<'_, T>
where
    T: Element + flatbuffers::Push + Copy,
    T::Output: 'static,
{
    type Output<'a> =
        flatbuffers::WIPOffset<flatbuffers::Vector<'a, <T as flatbuffers::Push>::Output>>;

    fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
        match self.as_slice() {
            // contiguous array
            Ok(slice) => builder.create_vector(slice),
            // non contiguous array fallback (copies to rust vec)
            Err(_) => {
                let values: Vec<T> = self.as_array().iter().copied().collect();
                builder.create_vector(&values)
            }
        }
    }
}
