use proc_macro::TokenStream;
use quote::{format_ident, quote, quote_spanned};
use syn::{Attribute, DataEnum, DataStruct, Ident};
use syn::{DeriveInput, Error, Token, parse_macro_input, spanned::Spanned};

use syn::parse::{Parse, ParseStream};

mod kw {
    syn::custom_keyword!(variant);
    syn::custom_keyword!(discriminant);
    syn::custom_keyword!(wrap);
    syn::custom_keyword!(flatbuffers_name);
    syn::custom_keyword!(transparent);
}

#[derive(Clone, Debug)]
enum SerialiseFieldAttribute {
    Variant,
    Wrap,
    FlatbuffersName(syn::Ident),
}

impl Parse for SerialiseFieldAttribute {
    fn parse(input: ParseStream) -> Result<Self, Error> {
        let lookahead = input.lookahead1();
        if lookahead.peek(kw::variant) {
            input.parse::<kw::variant>()?;
            Ok(SerialiseFieldAttribute::Variant)
        } else if lookahead.peek(kw::wrap) {
            input.parse::<kw::wrap>()?;
            Ok(SerialiseFieldAttribute::Wrap)
        } else if lookahead.peek(kw::flatbuffers_name) {
            input.parse::<kw::flatbuffers_name>()?;
            input.parse::<Token![=]>()?;
            input.parse().map(SerialiseFieldAttribute::FlatbuffersName)
        } else {
            Err(lookahead.error())
        }
    }
}

#[derive(Clone, Default, Debug)]
struct SerialiseFieldAttributes {
    variant: bool,
    wrap: bool,
    flatbuffers_name: Option<syn::Ident>,
}

impl SerialiseFieldAttributes {
    fn add_attribute(&mut self, a: &syn::Attribute) -> Result<(), Error> {
        let Some(attr_ident) = a.path().get_ident() else {
            return Ok(());
        };
        if attr_ident != "serialise" {
            return Ok(());
        }

        let attr: SerialiseFieldAttribute = a.parse_args()?;

        match attr {
            SerialiseFieldAttribute::Variant => self.variant = true,
            SerialiseFieldAttribute::Wrap => self.wrap = true,
            SerialiseFieldAttribute::FlatbuffersName(ident) => self.flatbuffers_name = Some(ident),
        }

        Ok(())
    }
}

#[derive(Clone, Debug)]
enum SerialiseStructAttribute {
    Wrap,
    FlatbuffersName(syn::Ident),
}

impl Parse for SerialiseStructAttribute {
    fn parse(input: ParseStream) -> Result<Self, Error> {
        let lookahead = input.lookahead1();
        if lookahead.peek(kw::wrap) {
            input.parse::<kw::wrap>()?;
            Ok(SerialiseStructAttribute::Wrap)
        } else if lookahead.peek(kw::flatbuffers_name) {
            input.parse::<kw::flatbuffers_name>()?;
            input.parse::<Token![=]>()?;
            input.parse().map(SerialiseStructAttribute::FlatbuffersName)
        } else {
            Err(lookahead.error())
        }
    }
}

#[derive(Clone, Default, Debug)]
struct SerialiseStructAttributes {
    flatbuffers_name: Option<syn::Ident>,
    wrap: bool,
}

impl SerialiseStructAttributes {
    fn add_attribute(&mut self, a: &syn::Attribute) -> Result<(), Error> {
        let Some(attr_ident) = a.path().get_ident() else {
            return Ok(());
        };
        if attr_ident != "serialise" {
            return Ok(());
        }

        let attr: SerialiseStructAttribute = a.parse_args()?;

        match attr {
            SerialiseStructAttribute::FlatbuffersName(ident) => self.flatbuffers_name = Some(ident),
            SerialiseStructAttribute::Wrap => self.wrap = true,
        }

        Ok(())
    }
}
#[derive(Clone, Debug)]
enum SerialiseEnumAttribute {
    Wrap,
    Transparent,
    FlatbuffersName(syn::Ident),
    Discriminant(syn::Ident),
}

impl Parse for SerialiseEnumAttribute {
    fn parse(input: ParseStream) -> Result<Self, Error> {
        let lookahead = input.lookahead1();
        if lookahead.peek(kw::wrap) {
            input.parse::<kw::wrap>()?;
            Ok(SerialiseEnumAttribute::Wrap)
        } else if lookahead.peek(kw::transparent) {
            input.parse::<kw::transparent>()?;
            Ok(SerialiseEnumAttribute::Transparent)
        } else if lookahead.peek(kw::flatbuffers_name) {
            input.parse::<kw::flatbuffers_name>()?;
            input.parse::<Token![=]>()?;
            input.parse().map(SerialiseEnumAttribute::FlatbuffersName)
        } else if lookahead.peek(kw::discriminant) {
            input.parse::<kw::discriminant>()?;
            input.parse::<Token![=]>()?;
            input.parse().map(SerialiseEnumAttribute::Discriminant)
        } else {
            Err(lookahead.error())
        }
    }
}

#[derive(Clone, Default, Debug)]
struct SerialiseEnumAttributes {
    flatbuffers_name: Option<syn::Ident>,
    discriminant: Option<syn::Ident>,
    wrap: bool,
    transparent: bool,
}

impl SerialiseEnumAttributes {
    fn add_attribute(&mut self, a: &syn::Attribute) -> Result<(), Error> {
        let Some(attr_ident) = a.path().get_ident() else {
            return Ok(());
        };
        if attr_ident != "serialise" {
            return Ok(());
        }

        let attr: SerialiseEnumAttribute = a.parse_args()?;

        match attr {
            SerialiseEnumAttribute::FlatbuffersName(ident) => self.flatbuffers_name = Some(ident),
            SerialiseEnumAttribute::Discriminant(ident) => self.discriminant = Some(ident),
            SerialiseEnumAttribute::Wrap => self.wrap = true,
            SerialiseEnumAttribute::Transparent => self.transparent = true,
        }

        Ok(())
    }
}

#[proc_macro_derive(Serialise, attributes(serialise))]
pub fn derive_serialise(input: TokenStream) -> TokenStream {
    // Parse the input tokens into a syntax tree
    let input = parse_macro_input!(input as DeriveInput);

    match do_derive_serialise(input) {
        Ok(tokens) => tokens,
        Err(e) => TokenStream::from(e.into_compile_error()),
    }
}

fn do_derive_serialise(input: DeriveInput) -> Result<TokenStream, Error> {
    let name = &input.ident;

    match input.data {
        syn::Data::Struct(data_struct) => {
            do_derive_serialise_struct(name, data_struct, &input.attrs)
        }
        syn::Data::Enum(data_enum) => do_derive_serialise_enum(name, data_enum, &input.attrs),
        _ => Err(Error::new_spanned(
            input,
            "#[derive(Serialise)] is not supported for rust unions",
        )),
    }
}

fn do_derive_serialise_struct(
    name: &Ident,
    input: DataStruct,
    attrs: &[Attribute],
) -> Result<TokenStream, Error> {
    let mut attributes = SerialiseStructAttributes::default();
    for attr in attrs {
        attributes.add_attribute(attr)?;
    }
    let fields = input.fields;

    let fields_named = match fields {
        syn::Fields::Named(fields_named) => fields_named,
        _ => {
            return Err(Error::new_spanned(
                fields,
                "#[derive(Serialise)] is only supported for structs with named fields",
            ));
        }
    };

    let generated_code = fields_named
        .named
        .iter()
        .map(|field| {
            let fname = field.ident.as_ref().ok_or_else(|| Error::new_spanned(field, "expected named field"))?;
            let mut field_attrs = SerialiseFieldAttributes::default();
            for a in field.attrs.iter() {
                attrs.add_attribute(a)?;
            }
            let fb_name = attrs.flatbuffers_name.as_ref().unwrap_or(fname);

            let code = if attrs.variant {
                let fbname_type = format_ident!("{fb_name}_type");
                let assignment = quote_spanned! {
                    field.span() =>
                    let #fbname_type = self.#fname.discriminant();
                    let #fname = self.#fname.serialise(builder);
                };
                let initialiser = quote_spanned! { field.span() => #fb_name: #fname.serialise_coerce(),
                #fbname_type: #fbname_type };
                (assignment, initialiser)
            } else {
                let assignment =
                    quote_spanned! { field.span() => let #fname = self.#fname.serialise(builder);};
                let initialiser = quote_spanned! { field.span() => #fb_name: #fname.serialise_coerce() };
                (assignment, initialiser)
            };

            Ok(code)
        })
        .collect::<Result<Vec<_>, Error>>()?;

    let (assignments, initialisers): (Vec<_>, Vec<_>) = generated_code.into_iter().unzip();

    let fb_name = attributes.flatbuffers_name.unwrap_or(name.clone());
    let args_ident = format_ident!("{}Args", fb_name);
    let expanded = quote! {
        impl crate::serialise::Serialise for #name {
            type Output<'a> = ::flatbuffers::WIPOffset<fb::#fb_name<'a>>;
            fn serialise<'a>(&self, builder: &mut ::flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
                #(#assignments)*


                let __args = fb::#args_ident {
                    #(#initialisers,)*
                    ..Default::default()
                };
                fb::#fb_name::create(builder, &__args)
            }
        }
    };

    Ok(TokenStream::from(expanded))
}

fn do_derive_serialise_enum(
    name: &Ident,
    input: DataEnum,
    attrs: &[Attribute],
) -> Result<TokenStream, Error> {
    let mut attributes = SerialiseEnumAttributes::default();
    for attr in attrs {
        attributes.add_attribute(attr)?;
    }

    let var_arms = input.variants.into_iter().map(|var| {
        match &var.fields {
            syn::Fields::Unnamed(f) => {
                if f.unnamed.len() != 1 {
                    return Err(Error::new_spanned(
                        f,
                        "#[derive(Serialise)] is only supported for enums with newtype variants",
                    ));
                }
            }
            _ => {
                return Err(Error::new_spanned(
                    var.fields,
                    "#[derive(Serialise)] is only supported for enums with newtype variants",
                ));
            }
        };

        let vname = &var.ident;

        let mut var_attrs = SerialiseFieldAttributes::default();
        for a in var.attrs.iter() {
            var_attrs.add_attribute(a)?;
        }

        let fb_name = var_attrs.flatbuffers_name.unwrap_or(vname.clone());
        let args_ident = format_ident!("{}Args", fb_name);


        let disc_arm = if attributes.transparent {
            quote_spanned! { var.span() => Self::#vname(inner) => {
            inner.discriminant()
        } }} else {
            quote_spanned! { var.span() => Self::#vname(_) => {
            Self::Disc::#fb_name
        } }};

        let offset_arm = if attributes.transparent {
            quote_spanned! { var.span() => Self::#vname(item) => {
                item.serialise(builder)
            } }
        } else if var_attrs.wrap {
            quote_spanned! { var.span() => Self::#vname(item) => {
                let value = item.serialise(builder);
                let _args = fb::#args_ident { value: value.serialise_coerce() };
                let offset = fb::#fb_name::create(builder, &_args);
                offset.as_union_value()
            } }
        } else {
            quote_spanned! { var.span() => Self::#vname(item) => {
                item.serialise(builder).as_union_value()
            } }
        };

        Ok((disc_arm, offset_arm))
    }).collect::<Result<Vec<_>, _>>()?;

    let (disc_arms, offset_arms): (Vec<_>, Vec<_>) = var_arms.into_iter().unzip();

    let serialise_impl = if attributes.wrap {
        let fb_name = attributes.flatbuffers_name.unwrap_or(name.clone());
        let args_ident = format_ident!("{}Args", fb_name);
        quote! {
            impl crate::serialise::Serialise for #name {
            type Output<'a> = ::flatbuffers::WIPOffset<fb::#fb_name<'a>>;
                fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
                    let value_type = self.discriminant();

                    let value = match self {
                        #(#offset_arms)*
                    };

                    let __args = fb::#args_ident {
                        value: value.serialise_coerce(),
                        value_type: value_type.serialise_coerce(),
                    };
                    fb::#fb_name::create(builder, &__args)
                }
            }
        }
    } else {
        quote! {
            impl crate::serialise::Serialise for #name {
                type Output<'a> = ::flatbuffers::WIPOffset<::flatbuffers::UnionWIPOffset>;
                fn serialise<'a>(&self, builder: &mut flatbuffers::FlatBufferBuilder<'a>) -> Self::Output<'a> {
                    match self {
                        #(#offset_arms)*
                    }
                }
            }
        }
    };

    let disc_name = attributes.discriminant.unwrap_or(name.clone());

    let discriminant_impl = quote! {
        impl crate::serialise::Discriminant for #name {
            type Disc = fb::#disc_name;

            fn discriminant(&self) -> Self::Disc {
                match self {
                    #(#disc_arms)*
                }
            }
        }
    };

    let expanded = quote! {
        #serialise_impl

        #discriminant_impl
    };

    Ok(TokenStream::from(expanded))
}
