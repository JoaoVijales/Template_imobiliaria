"""
Extended unit tests for PropertyService covering methods not previously tested:
- get_similar_properties()
- record_inquiry()
- _apply_filters_to_qs() (internal helper)
"""
from decimal import Decimal

import pytest

from apps.properties.models import Property, PropertyInquiry
from apps.properties.services import PropertyService
from tests.fixtures.factories import PropertyFactory, PropertyInquiryFactory


@pytest.mark.django_db
class TestPropertyServiceGetSimilarProperties:
    """Tests for PropertyService.get_similar_properties()."""

    def test_should_return_properties_with_same_type_and_city(self):
        target = PropertyFactory(
            property_type='house',
            city='Curitiba',
            is_active=True,
        )
        similar = PropertyFactory(
            property_type='house',
            city='Curitiba',
            is_active=True,
        )
        different_type = PropertyFactory(
            property_type='apartment',
            city='Curitiba',
            is_active=True,
        )
        different_city = PropertyFactory(
            property_type='house',
            city='São Paulo',
            is_active=True,
        )

        service = PropertyService()
        results = list(service.get_similar_properties(target))
        result_pks = [p.pk for p in results]

        assert similar.pk in result_pks
        assert different_type.pk not in result_pks
        assert different_city.pk not in result_pks

    def test_should_exclude_the_target_property_itself(self):
        target = PropertyFactory(
            property_type='house',
            city='Florianópolis',
            is_active=True,
        )
        # Create a similar one so the query returns results
        PropertyFactory(
            property_type='house',
            city='Florianópolis',
            is_active=True,
        )

        service = PropertyService()
        results = list(service.get_similar_properties(target))
        result_pks = [p.pk for p in results]

        assert target.pk not in result_pks

    def test_should_respect_limit_parameter(self):
        target = PropertyFactory(property_type='apartment', city='Porto Alegre', is_active=True)
        PropertyFactory.create_batch(
            6,
            property_type='apartment',
            city='Porto Alegre',
            is_active=True,
        )

        service = PropertyService()
        results = list(service.get_similar_properties(target, limit=3))
        assert len(results) <= 3

    def test_should_exclude_inactive_properties(self):
        target = PropertyFactory(property_type='land', city='Brasília', is_active=True)
        inactive_similar = PropertyFactory(
            property_type='land',
            city='Brasília',
            is_active=False,
        )

        service = PropertyService()
        results = list(service.get_similar_properties(target))
        result_pks = [p.pk for p in results]

        assert inactive_similar.pk not in result_pks

    def test_should_return_empty_queryset_when_no_similar_exist(self):
        target = PropertyFactory(property_type='rural', city='Manaus', is_active=True)

        service = PropertyService()
        results = list(service.get_similar_properties(target))
        assert results == []


@pytest.mark.django_db
class TestPropertyServiceRecordInquiry:
    """Tests for PropertyService.record_inquiry()."""

    def test_should_create_inquiry_with_correct_fields(self):
        prop = PropertyFactory(is_active=True)
        form_data = {
            'name': 'Ana Lima',
            'email': 'ana@example.com',
            'phone': '(11) 98765-4321',
            'message': 'Quero agendar uma visita.',
        }

        service = PropertyService()
        inquiry = service.record_inquiry(prop.pk, form_data)

        assert inquiry.pk is not None
        assert inquiry.property == prop
        assert inquiry.name == 'Ana Lima'
        assert inquiry.email == 'ana@example.com'
        assert inquiry.phone == '(11) 98765-4321'
        assert inquiry.message == 'Quero agendar uma visita.'

    def test_should_return_property_inquiry_instance(self):
        prop = PropertyFactory(is_active=True)
        form_data = {
            'name': 'Carlos Andrade',
            'email': 'carlos@example.com',
            'message': 'Tenho interesse.',
        }

        service = PropertyService()
        result = service.record_inquiry(prop.pk, form_data)

        assert isinstance(result, PropertyInquiry)

    def test_should_persist_inquiry_to_database(self):
        prop = PropertyFactory(is_active=True)
        form_data = {
            'name': 'Fernanda',
            'email': 'fernanda@example.com',
            'message': 'Mensagem persistida.',
        }

        service = PropertyService()
        inquiry = service.record_inquiry(prop.pk, form_data)

        assert PropertyInquiry.objects.filter(pk=inquiry.pk).exists()

    def test_should_default_phone_to_empty_string_when_not_provided(self):
        prop = PropertyFactory(is_active=True)
        form_data = {
            'name': 'Pedro',
            'email': 'pedro@example.com',
            'message': 'Sem telefone.',
            # phone intentionally absent
        }

        service = PropertyService()
        inquiry = service.record_inquiry(prop.pk, form_data)

        assert inquiry.phone == ''

    def test_should_raise_when_property_does_not_exist(self):
        service = PropertyService()
        form_data = {
            'name': 'Ghost',
            'email': 'ghost@example.com',
            'message': 'Propriedade inexistente.',
        }

        with pytest.raises(Property.DoesNotExist):
            service.record_inquiry(99999999, form_data)


@pytest.mark.django_db
class TestPropertyServiceApplyFiltersToQs:
    """Tests for PropertyService._apply_filters_to_qs() internal helper."""

    def _get_base_qs(self):
        return Property.objects.active()

    def test_should_filter_by_listing_type(self):
        sale = PropertyFactory(listing_type='sale', is_active=True)
        rent = PropertyFactory(listing_type='rent', is_active=True)

        service = PropertyService()
        qs = service._apply_filters_to_qs(self._get_base_qs(), {'listing_type': 'sale'})
        pks = list(qs.values_list('pk', flat=True))

        assert sale.pk in pks
        assert rent.pk not in pks

    def test_should_filter_by_property_type(self):
        house = PropertyFactory(property_type='house', is_active=True)
        apt = PropertyFactory(property_type='apartment', is_active=True)

        service = PropertyService()
        qs = service._apply_filters_to_qs(self._get_base_qs(), {'property_type': 'house'})
        pks = list(qs.values_list('pk', flat=True))

        assert house.pk in pks
        assert apt.pk not in pks

    def test_should_filter_by_city_case_insensitive(self):
        prop = PropertyFactory(city='Recife', is_active=True)
        other = PropertyFactory(city='Salvador', is_active=True)

        service = PropertyService()
        qs = service._apply_filters_to_qs(self._get_base_qs(), {'city': 'recife'})
        pks = list(qs.values_list('pk', flat=True))

        assert prop.pk in pks
        assert other.pk not in pks

    def test_should_filter_by_min_price(self):
        cheap = PropertyFactory(price=Decimal('50000.00'), is_active=True)
        expensive = PropertyFactory(price=Decimal('600000.00'), is_active=True)

        service = PropertyService()
        qs = service._apply_filters_to_qs(self._get_base_qs(), {'min_price': Decimal('300000.00')})
        pks = list(qs.values_list('pk', flat=True))

        assert expensive.pk in pks
        assert cheap.pk not in pks

    def test_should_filter_by_max_price(self):
        cheap = PropertyFactory(price=Decimal('80000.00'), is_active=True)
        expensive = PropertyFactory(price=Decimal('900000.00'), is_active=True)

        service = PropertyService()
        qs = service._apply_filters_to_qs(self._get_base_qs(), {'max_price': Decimal('200000.00')})
        pks = list(qs.values_list('pk', flat=True))

        assert cheap.pk in pks
        assert expensive.pk not in pks

    def test_should_filter_by_min_bedrooms(self):
        small = PropertyFactory(bedrooms=1, is_active=True)
        large = PropertyFactory(bedrooms=4, is_active=True)

        service = PropertyService()
        qs = service._apply_filters_to_qs(self._get_base_qs(), {'min_bedrooms': 3})
        pks = list(qs.values_list('pk', flat=True))

        assert large.pk in pks
        assert small.pk not in pks

    def test_should_return_unfiltered_qs_when_no_filters(self):
        PropertyFactory.create_batch(3, is_active=True)

        service = PropertyService()
        qs = service._apply_filters_to_qs(self._get_base_qs(), {})

        assert qs.count() == 3
