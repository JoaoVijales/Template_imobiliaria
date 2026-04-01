"""
Unit tests for PropertyService — all repository calls are mocked so
these tests do not require a database.
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.http import Http404

from apps.properties.services import (
    HOMEPAGE_FEATURED_LIMIT,
    HOMEPAGE_RECENT_LIMIT,
    PropertyService,
)
from tests.fixtures.factories import PropertyFactory, PropertyInquiryFactory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_service(mock_repo=None):
    """Return a PropertyService wired to the given (or a fresh) mock repo."""
    if mock_repo is None:
        mock_repo = MagicMock()
    return PropertyService(repository=mock_repo), mock_repo


# ---------------------------------------------------------------------------
# TestPropertyService
# ---------------------------------------------------------------------------


class TestPropertyService:
    """Tests for PropertyService business logic using mocked repositories."""

    # ------------------------------------------------------------------
    # get_homepage_data
    # ------------------------------------------------------------------

    def test_get_homepage_data_calls_get_featured(self):
        service, mock_repo = _make_service()
        mock_repo.get_featured.return_value = MagicMock()
        mock_repo.get_all_active.return_value = MagicMock()

        service.get_homepage_data()

        mock_repo.get_featured.assert_called_once()

    def test_get_homepage_data_calls_get_all_active(self):
        service, mock_repo = _make_service()
        mock_repo.get_featured.return_value = MagicMock()
        mock_repo.get_all_active.return_value = MagicMock()

        service.get_homepage_data()

        mock_repo.get_all_active.assert_called_once()

    def test_get_homepage_data_returns_featured_and_recent_keys(self):
        service, mock_repo = _make_service()
        featured_qs = MagicMock()
        recent_qs = MagicMock()
        mock_repo.get_featured.return_value.__getitem__ = lambda s, x: featured_qs
        mock_repo.get_all_active.return_value.__getitem__ = lambda s, x: recent_qs

        result = service.get_homepage_data()

        assert 'featured' in result
        assert 'recent' in result

    def test_get_homepage_data_limits_featured_to_homepage_featured_limit(self):
        service, mock_repo = _make_service()
        featured_mock = MagicMock()
        mock_repo.get_featured.return_value = featured_mock
        mock_repo.get_all_active.return_value = MagicMock()

        service.get_homepage_data()

        # Verify slice [:HOMEPAGE_FEATURED_LIMIT] was called on the queryset
        featured_mock.__getitem__.assert_called_with(slice(None, HOMEPAGE_FEATURED_LIMIT, None))

    def test_get_homepage_data_limits_recent_to_homepage_recent_limit(self):
        service, mock_repo = _make_service()
        recent_mock = MagicMock()
        mock_repo.get_featured.return_value = MagicMock()
        mock_repo.get_all_active.return_value = recent_mock

        service.get_homepage_data()

        recent_mock.__getitem__.assert_called_with(slice(None, HOMEPAGE_RECENT_LIMIT, None))

    # ------------------------------------------------------------------
    # get_detail
    # ------------------------------------------------------------------

    def test_get_detail_returns_property_when_found(self):
        service, mock_repo = _make_service()
        fake_prop = MagicMock()
        mock_repo.get_by_slug.return_value = fake_prop

        result = service.get_detail('some-valid-slug')

        assert result is fake_prop
        mock_repo.get_by_slug.assert_called_once_with('some-valid-slug')

    def test_get_detail_raises_404_when_property_not_found(self):
        service, mock_repo = _make_service()
        mock_repo.get_by_slug.return_value = None

        with pytest.raises(Http404):
            service.get_detail('slug-that-does-not-exist')

    # ------------------------------------------------------------------
    # get_listing
    # ------------------------------------------------------------------

    def test_get_listing_delegates_to_get_filtered_when_no_query(self):
        service, mock_repo = _make_service()
        filters = {'listing_type': 'sale', 'city': 'Manaus'}

        service.get_listing(filters.copy())

        mock_repo.get_filtered.assert_called_once_with({'listing_type': 'sale', 'city': 'Manaus'})

    def test_get_listing_delegates_to_search_when_query_present(self):
        service, mock_repo = _make_service()
        mock_repo.search.return_value = MagicMock()
        filters = {'q': 'cobertura', 'listing_type': 'sale'}

        service.get_listing(filters.copy())

        mock_repo.search.assert_called_once_with('cobertura')

    def test_get_listing_does_not_call_get_filtered_when_only_query(self):
        service, mock_repo = _make_service()
        mock_repo.search.return_value = MagicMock()

        service.get_listing({'q': 'cobertura'})

        mock_repo.get_filtered.assert_not_called()

    # ------------------------------------------------------------------
    # record_inquiry
    # ------------------------------------------------------------------

    @pytest.mark.django_db
    def test_record_inquiry_creates_inquiry_with_correct_data(self):
        prop = PropertyFactory(is_active=True)
        form_data = {
            'name': 'Maria Oliveira',
            'email': 'maria@example.com',
            'phone': '(11) 91234-5678',
            'message': 'Gostaria de agendar uma visita.',
        }

        service = PropertyService()
        inquiry = service.record_inquiry(property_id=prop.pk, form_data=form_data)

        assert inquiry.pk is not None
        assert inquiry.property_id == prop.pk
        assert inquiry.name == 'Maria Oliveira'
        assert inquiry.email == 'maria@example.com'
        assert inquiry.phone == '(11) 91234-5678'
        assert inquiry.message == 'Gostaria de agendar uma visita.'

    @pytest.mark.django_db
    def test_record_inquiry_creates_inquiry_without_optional_phone(self):
        prop = PropertyFactory(is_active=True)
        form_data = {
            'name': 'Carlos Souza',
            'email': 'carlos@example.com',
            'message': 'Quanto custa o condomínio?',
        }

        service = PropertyService()
        inquiry = service.record_inquiry(property_id=prop.pk, form_data=form_data)

        assert inquiry.phone == ''

    @pytest.mark.django_db
    def test_record_inquiry_raises_does_not_exist_for_missing_property(self):
        from apps.properties.models import Property

        service = PropertyService()
        form_data = {
            'name': 'Test',
            'email': 'test@example.com',
            'message': 'Test message',
        }

        with pytest.raises(Property.DoesNotExist):
            service.record_inquiry(property_id=999999, form_data=form_data)

    @pytest.mark.django_db
    def test_record_inquiry_sets_is_read_false_by_default(self):
        prop = PropertyFactory(is_active=True)
        form_data = {
            'name': 'Ana Lima',
            'email': 'ana@example.com',
            'message': 'Informações sobre o imóvel.',
        }

        service = PropertyService()
        inquiry = service.record_inquiry(property_id=prop.pk, form_data=form_data)

        assert inquiry.is_read is False
