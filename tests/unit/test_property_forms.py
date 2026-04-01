"""
Unit tests for PropertySearchForm and PropertyInquiryForm.
These tests exercise form validation without touching the database.
"""
from decimal import Decimal

import pytest

from apps.properties.forms import PropertyInquiryForm, PropertySearchForm
from apps.properties.models import ListingType, PropertyType


# ---------------------------------------------------------------------------
# TestPropertySearchForm
# ---------------------------------------------------------------------------


class TestPropertySearchForm:
    """Tests for the property listing/search filter form."""

    def test_form_is_valid_with_no_fields_submitted(self):
        form = PropertySearchForm(data={})
        assert form.is_valid(), form.errors

    def test_form_is_valid_with_all_fields_filled(self):
        data = {
            'q': 'apartamento',
            'listing_type': ListingType.SALE,
            'property_type': PropertyType.APARTMENT,
            'city': 'São Paulo',
            'min_price': '100000',
            'max_price': '500000',
            'min_bedrooms': '2',
        }
        form = PropertySearchForm(data=data)
        assert form.is_valid(), form.errors

    def test_form_is_valid_with_partial_fields(self):
        data = {'city': 'Curitiba', 'listing_type': ListingType.RENT}
        form = PropertySearchForm(data=data)
        assert form.is_valid(), form.errors

    def test_price_fields_accept_decimal_values(self):
        data = {'min_price': '199999.99', 'max_price': '999999.50'}
        form = PropertySearchForm(data=data)
        assert form.is_valid(), form.errors
        assert form.cleaned_data['min_price'] == Decimal('199999.99')
        assert form.cleaned_data['max_price'] == Decimal('999999.50')

    def test_price_fields_reject_negative_values(self):
        data = {'min_price': '-1000'}
        form = PropertySearchForm(data=data)
        assert not form.is_valid()
        assert 'min_price' in form.errors

    def test_min_bedrooms_rejects_negative_values(self):
        data = {'min_bedrooms': '-1'}
        form = PropertySearchForm(data=data)
        assert not form.is_valid()
        assert 'min_bedrooms' in form.errors

    def test_listing_type_rejects_invalid_choice(self):
        data = {'listing_type': 'barter'}
        form = PropertySearchForm(data=data)
        assert not form.is_valid()
        assert 'listing_type' in form.errors

    def test_property_type_rejects_invalid_choice(self):
        data = {'property_type': 'yacht'}
        form = PropertySearchForm(data=data)
        assert not form.is_valid()
        assert 'property_type' in form.errors

    def test_get_filters_omits_empty_values(self):
        data = {'q': '', 'city': '', 'listing_type': '', 'property_type': ''}
        form = PropertySearchForm(data=data)
        assert form.is_valid()
        filters = form.get_filters()
        assert filters == {}

    def test_get_filters_returns_only_submitted_values(self):
        data = {'city': 'Brasília', 'listing_type': ListingType.SALE}
        form = PropertySearchForm(data=data)
        assert form.is_valid()
        filters = form.get_filters()
        assert filters == {'city': 'Brasília', 'listing_type': 'sale'}

    def test_get_filters_strips_whitespace_from_text_fields(self):
        data = {'q': '  loft  ', 'city': '  Porto Alegre  '}
        form = PropertySearchForm(data=data)
        assert form.is_valid()
        filters = form.get_filters()
        assert filters['q'] == 'loft'
        assert filters['city'] == 'Porto Alegre'

    def test_get_filters_includes_price_bounds_when_provided(self):
        data = {'min_price': '200000', 'max_price': '800000'}
        form = PropertySearchForm(data=data)
        assert form.is_valid()
        filters = form.get_filters()
        assert filters['min_price'] == Decimal('200000')
        assert filters['max_price'] == Decimal('800000')

    def test_get_filters_includes_min_bedrooms_when_provided(self):
        data = {'min_bedrooms': '3'}
        form = PropertySearchForm(data=data)
        assert form.is_valid()
        filters = form.get_filters()
        assert filters['min_bedrooms'] == 3


# ---------------------------------------------------------------------------
# TestPropertyInquiryForm
# ---------------------------------------------------------------------------


class TestPropertyInquiryForm:
    """Tests for the contact / inquiry form on the property detail page."""

    def test_form_is_valid_with_all_required_fields(self):
        data = {
            'name': 'Roberto Ferreira',
            'email': 'roberto@example.com',
            'phone': '(21) 98765-4321',
            'message': 'Gostaria de agendar uma visita ao imóvel.',
        }
        form = PropertyInquiryForm(data=data)
        assert form.is_valid(), form.errors

    def test_form_requires_name(self):
        data = {
            'email': 'test@example.com',
            'message': 'Mensagem de teste.',
        }
        form = PropertyInquiryForm(data=data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_form_requires_email(self):
        data = {
            'name': 'Test User',
            'message': 'Mensagem de teste.',
        }
        form = PropertyInquiryForm(data=data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_form_requires_message(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
        }
        form = PropertyInquiryForm(data=data)
        assert not form.is_valid()
        assert 'message' in form.errors

    def test_form_phone_is_optional(self):
        data = {
            'name': 'Luciana Mendes',
            'email': 'luciana@example.com',
            'message': 'Pode me enviar mais fotos?',
            # phone intentionally omitted
        }
        form = PropertyInquiryForm(data=data)
        assert form.is_valid(), form.errors

    def test_form_rejects_invalid_email(self):
        data = {
            'name': 'Test User',
            'email': 'not-an-email',
            'message': 'Mensagem de teste.',
        }
        form = PropertyInquiryForm(data=data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_form_rejects_email_without_domain(self):
        data = {
            'name': 'Test User',
            'email': 'user@',
            'message': 'Mensagem de teste.',
        }
        form = PropertyInquiryForm(data=data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_form_rejects_empty_name(self):
        data = {
            'name': '',
            'email': 'valid@example.com',
            'message': 'Mensagem de teste.',
        }
        form = PropertyInquiryForm(data=data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_form_rejects_empty_message(self):
        data = {
            'name': 'Test User',
            'email': 'valid@example.com',
            'message': '',
        }
        form = PropertyInquiryForm(data=data)
        assert not form.is_valid()
        assert 'message' in form.errors

    def test_form_is_invalid_when_completely_empty(self):
        form = PropertyInquiryForm(data={})
        assert not form.is_valid()

    def test_form_fields_are_limited_to_expected_set(self):
        form = PropertyInquiryForm()
        assert set(form.fields.keys()) == {'name', 'email', 'phone', 'message'}
