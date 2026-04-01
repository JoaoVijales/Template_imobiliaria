"""
Unit tests for the Property, PropertyImage, and PropertyInquiry models,
as well as the PropertyManager / PropertyQuerySet.
"""
from decimal import Decimal

import pytest

from apps.properties.models import ListingType, Property, PropertyType
from tests.fixtures.factories import (
    PropertyFactory,
    PropertyImageFactory,
    PropertyInquiryFactory,
)


# ---------------------------------------------------------------------------
# TestPropertyModel
# ---------------------------------------------------------------------------


class TestPropertyModel:
    """Tests for the Property model instance behaviour."""

    @pytest.mark.django_db
    def test_should_return_str_as_title(self):
        prop = PropertyFactory(title='Apartamento no Centro')
        assert str(prop) == 'Apartamento no Centro'

    @pytest.mark.django_db
    def test_should_calculate_price_per_sqm_correctly(self):
        prop = PropertyFactory(price=Decimal('300000.00'), area=Decimal('100.00'))
        assert prop.price_per_sqm == Decimal('3000.00')

    @pytest.mark.django_db
    def test_should_return_none_for_price_per_sqm_when_area_is_zero(self):
        prop = PropertyFactory(price=Decimal('200000.00'), area=Decimal('0.00'))
        assert prop.price_per_sqm is None

    @pytest.mark.django_db
    def test_should_return_main_image_when_exists(self):
        prop = PropertyFactory()
        secondary = PropertyImageFactory(property=prop, is_main=False, order=0)
        main_img = PropertyImageFactory(property=prop, is_main=True, order=1)
        result = prop.main_image
        assert result.pk == main_img.pk

    @pytest.mark.django_db
    def test_should_return_first_image_by_order_when_no_main_flag_set(self):
        prop = PropertyFactory()
        first_by_order = PropertyImageFactory(property=prop, is_main=False, order=0)
        PropertyImageFactory(property=prop, is_main=False, order=1)
        result = prop.main_image
        assert result.pk == first_by_order.pk

    @pytest.mark.django_db
    def test_should_return_none_for_main_image_when_no_images(self):
        prop = PropertyFactory()
        assert prop.main_image is None

    @pytest.mark.django_db
    def test_should_generate_absolute_url(self):
        prop = PropertyFactory(slug='casa-em-sao-paulo-1234')
        url = prop.get_absolute_url()
        # URL is generated via reverse('properties:detail', kwargs={'slug': ...})
        assert 'casa-em-sao-paulo-1234' in url
        assert url.endswith('/')

    @pytest.mark.django_db
    def test_should_default_is_active_to_true(self):
        # Create via ORM directly to verify model-level default, not factory override
        prop = Property.objects.create(
            title='Test Active Default',
            slug='test-active-default-9999',
            description='Test',
            property_type=PropertyType.HOUSE,
            listing_type=ListingType.SALE,
            price=Decimal('500000.00'),
            area=Decimal('120.00'),
            address='Rua Test, 1',
            city='São Paulo',
            state='SP',
        )
        assert prop.is_active is True

    @pytest.mark.django_db
    def test_should_default_is_featured_to_false(self):
        prop = Property.objects.create(
            title='Test Featured Default',
            slug='test-featured-default-8888',
            description='Test',
            property_type=PropertyType.APARTMENT,
            listing_type=ListingType.RENT,
            price=Decimal('3000.00'),
            area=Decimal('60.00'),
            address='Rua Test, 2',
            city='Curitiba',
            state='PR',
        )
        assert prop.is_featured is False

    @pytest.mark.django_db
    def test_should_store_and_retrieve_price_per_sqm_with_decimal_precision(self):
        prop = PropertyFactory(price=Decimal('250000.00'), area=Decimal('75.00'))
        # 250000 / 75 = 3333.333...
        expected = Decimal('250000.00') / Decimal('75.00')
        assert prop.price_per_sqm == expected

    @pytest.mark.django_db
    def test_property_inquiry_str_contains_name_and_title(self):
        prop = PropertyFactory(title='Casa Bonita')
        inquiry = PropertyInquiryFactory(property=prop, name='João Silva')
        assert 'João Silva' in str(inquiry)
        assert 'Casa Bonita' in str(inquiry)

    @pytest.mark.django_db
    def test_property_image_str_contains_property_title(self):
        prop = PropertyFactory(title='Loft Moderno')
        image = PropertyImageFactory(property=prop, order=0)
        assert 'Loft Moderno' in str(image)


# ---------------------------------------------------------------------------
# TestPropertyManager
# ---------------------------------------------------------------------------


class TestPropertyManager:
    """Tests for PropertyManager and PropertyQuerySet methods."""

    @pytest.mark.django_db
    def test_active_queryset_excludes_inactive_properties(self):
        active = PropertyFactory(is_active=True)
        inactive = PropertyFactory(is_active=False)

        qs = Property.objects.active()

        pks = list(qs.values_list('pk', flat=True))
        assert active.pk in pks
        assert inactive.pk not in pks

    @pytest.mark.django_db
    def test_active_queryset_returns_all_active_properties(self):
        PropertyFactory.create_batch(3, is_active=True)
        PropertyFactory.create_batch(2, is_active=False)

        assert Property.objects.active().count() == 3

    @pytest.mark.django_db
    def test_featured_queryset_returns_only_featured_and_active(self):
        featured_active = PropertyFactory(is_featured=True, is_active=True)
        featured_inactive = PropertyFactory(is_featured=True, is_active=False)
        not_featured_active = PropertyFactory(is_featured=False, is_active=True)

        qs = Property.objects.featured()
        pks = list(qs.values_list('pk', flat=True))

        assert featured_active.pk in pks
        assert featured_inactive.pk not in pks
        assert not_featured_active.pk not in pks

    @pytest.mark.django_db
    def test_for_sale_returns_only_sale_listings(self):
        sale = PropertyFactory(listing_type='sale', is_active=True)
        rent = PropertyFactory(listing_type='rent', is_active=True)

        qs = Property.objects.for_sale()
        pks = list(qs.values_list('pk', flat=True))

        assert sale.pk in pks
        assert rent.pk not in pks

    @pytest.mark.django_db
    def test_for_sale_excludes_inactive_properties(self):
        inactive_sale = PropertyFactory(listing_type='sale', is_active=False)
        qs = Property.objects.for_sale()
        assert inactive_sale.pk not in list(qs.values_list('pk', flat=True))

    @pytest.mark.django_db
    def test_for_rent_returns_only_rent_listings(self):
        rent = PropertyFactory(listing_type='rent', is_active=True)
        sale = PropertyFactory(listing_type='sale', is_active=True)

        qs = Property.objects.for_rent()
        pks = list(qs.values_list('pk', flat=True))

        assert rent.pk in pks
        assert sale.pk not in pks

    @pytest.mark.django_db
    def test_for_rent_excludes_inactive_properties(self):
        inactive_rent = PropertyFactory(listing_type='rent', is_active=False)
        qs = Property.objects.for_rent()
        assert inactive_rent.pk not in list(qs.values_list('pk', flat=True))

    @pytest.mark.django_db
    def test_by_city_is_case_insensitive(self):
        # Use ASCII-only city to avoid SQLite collation limitations with accented chars
        prop = PropertyFactory(city='Curitiba', is_active=True)

        # Query with different casing variants — SQLite iexact supports ASCII case folding
        for variant in ('curitiba', 'CURITIBA', 'Curitiba', 'CuRiTiBa'):
            qs = Property.objects.by_city(variant)
            pks = list(qs.values_list('pk', flat=True))
            assert prop.pk in pks, f"Expected property found for city variant '{variant}'"

    @pytest.mark.django_db
    def test_by_city_does_not_return_other_cities(self):
        sp_prop = PropertyFactory(city='São Paulo', is_active=True)
        rj_prop = PropertyFactory(city='Rio de Janeiro', is_active=True)

        qs = Property.objects.by_city('São Paulo')
        pks = list(qs.values_list('pk', flat=True))

        assert sp_prop.pk in pks
        assert rj_prop.pk not in pks

    @pytest.mark.django_db
    def test_by_type_filters_by_property_type(self):
        house = PropertyFactory(property_type='house', is_active=True)
        apartment = PropertyFactory(property_type='apartment', is_active=True)

        qs = Property.objects.by_type('house')
        pks = list(qs.values_list('pk', flat=True))

        assert house.pk in pks
        assert apartment.pk not in pks
