"""
factory_boy factories for the properties app test suite.
"""
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from apps.properties.models import (
    ListingType,
    Property,
    PropertyImage,
    PropertyInquiry,
    PropertyType,
)

fake = Faker('pt_BR')


def _slugify(text: str) -> str:
    """Simple ASCII slug helper (avoids importing Django utils at module level)."""
    from django.utils.text import slugify
    return slugify(text)


class PropertyFactory(DjangoModelFactory):
    """Factory for creating Property test instances."""

    class Meta:
        model = Property

    title = factory.LazyFunction(lambda: f"Casa em {fake.city()}")
    slug = factory.LazyAttribute(
        lambda o: _slugify(o.title) + f"-{fake.pyint(min_value=1000, max_value=9999)}"
    )
    description = factory.LazyFunction(fake.paragraph)
    property_type = factory.Iterator([t[0] for t in PropertyType.choices])
    listing_type = factory.Iterator([t[0] for t in ListingType.choices])
    price = factory.LazyFunction(
        lambda: Decimal(str(fake.pyint(min_value=100_000, max_value=2_000_000)))
    )
    area = factory.LazyFunction(
        lambda: Decimal(str(fake.pyint(min_value=40, max_value=500)))
    )
    bedrooms = factory.LazyFunction(lambda: fake.pyint(min_value=1, max_value=5))
    bathrooms = factory.LazyFunction(lambda: fake.pyint(min_value=1, max_value=4))
    parking_spots = factory.LazyFunction(lambda: fake.pyint(min_value=0, max_value=3))
    address = factory.LazyFunction(fake.street_address)
    city = factory.LazyFunction(fake.city)
    state = factory.LazyFunction(lambda: fake.estado_sigla())
    neighborhood = factory.LazyFunction(fake.bairro)
    zipcode = factory.LazyFunction(fake.postcode)
    is_featured = False
    is_active = True


class PropertyImageFactory(DjangoModelFactory):
    """Factory for creating PropertyImage test instances."""

    class Meta:
        model = PropertyImage

    property = factory.SubFactory(PropertyFactory)
    # image field intentionally left blank; tests that need an actual file
    # should override with a SimpleUploadedFile or skip image validation.
    image = factory.django.ImageField(filename='test_image.jpg')
    caption = factory.LazyFunction(lambda: fake.sentence(nb_words=4))
    is_main = False
    order = factory.Sequence(lambda n: n)


class PropertyInquiryFactory(DjangoModelFactory):
    """Factory for creating PropertyInquiry test instances."""

    class Meta:
        model = PropertyInquiry

    property = factory.SubFactory(PropertyFactory)
    name = factory.LazyFunction(fake.name)
    email = factory.LazyFunction(fake.email)
    phone = factory.LazyFunction(fake.phone_number)
    message = factory.LazyFunction(fake.paragraph)
    is_read = False
