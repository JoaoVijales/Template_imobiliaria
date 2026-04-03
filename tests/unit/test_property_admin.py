"""
Unit tests for PropertyAdmin and PropertyInquiryAdmin.
Tests formatted_price display method and mark_as_read/mark_as_unread actions.
"""
from decimal import Decimal

import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from apps.properties.admin import PropertyAdmin, PropertyInquiryAdmin
from apps.properties.models import Property, PropertyInquiry
from tests.fixtures.factories import PropertyFactory, PropertyInquiryFactory


class TestPropertyAdminFormattedPrice:
    """Tests for PropertyAdmin.formatted_price() display method."""

    def setup_method(self):
        self.site = AdminSite()
        self.admin = PropertyAdmin(Property, self.site)

    @pytest.mark.django_db
    def test_formatted_price_contains_brl_symbol(self):
        prop = PropertyFactory(price=Decimal('1500000.00'))
        result = self.admin.formatted_price(prop)
        assert 'R$' in result

    @pytest.mark.django_db
    def test_formatted_price_formats_thousands_separator_correctly(self):
        prop = PropertyFactory(price=Decimal('1500000.00'))
        result = self.admin.formatted_price(prop)
        # Brazilian format: 1.500.000,00
        assert '1.500.000' in result

    @pytest.mark.django_db
    def test_formatted_price_formats_decimal_separator_correctly(self):
        prop = PropertyFactory(price=Decimal('250000.50'))
        result = self.admin.formatted_price(prop)
        # Decimal separator is a comma in Brazilian format
        assert ',50' in result

    @pytest.mark.django_db
    def test_formatted_price_for_round_value(self):
        prop = PropertyFactory(price=Decimal('500000.00'))
        result = self.admin.formatted_price(prop)
        assert 'R$' in result
        assert '500.000' in result

    @pytest.mark.django_db
    def test_formatted_price_for_small_value(self):
        prop = PropertyFactory(price=Decimal('1000.00'))
        result = self.admin.formatted_price(prop)
        assert 'R$' in result
        assert '1.000' in result


class TestPropertyInquiryAdminActions:
    """Tests for PropertyInquiryAdmin bulk actions mark_as_read and mark_as_unread."""

    def setup_method(self):
        self.site = AdminSite()
        self.admin = PropertyInquiryAdmin(PropertyInquiry, self.site)
        self.factory = RequestFactory()

    def _make_request(self):
        """Create a minimal request object for admin action calls."""
        request = self.factory.get('/')
        # Patch message_user to avoid MessagesMiddleware requirement
        self.admin.message_user = lambda *args, **kwargs: None
        return request

    @pytest.mark.django_db
    def test_mark_as_read_updates_all_selected_inquiries(self):
        inquiries = PropertyInquiryFactory.create_batch(3, is_read=False)
        pks = [i.pk for i in inquiries]
        qs = PropertyInquiry.objects.filter(pk__in=pks)

        self.admin.mark_as_read(self._make_request(), qs)

        assert PropertyInquiry.objects.filter(pk__in=pks, is_read=True).count() == 3

    @pytest.mark.django_db
    def test_mark_as_read_does_not_affect_unselected_inquiries(self):
        selected = PropertyInquiryFactory.create_batch(2, is_read=False)
        unselected = PropertyInquiryFactory(is_read=False)
        qs = PropertyInquiry.objects.filter(pk__in=[i.pk for i in selected])

        self.admin.mark_as_read(self._make_request(), qs)

        # Unselected inquiry should remain unread
        unselected.refresh_from_db()
        assert unselected.is_read is False

    @pytest.mark.django_db
    def test_mark_as_unread_updates_all_selected_inquiries(self):
        inquiries = PropertyInquiryFactory.create_batch(3, is_read=True)
        pks = [i.pk for i in inquiries]
        qs = PropertyInquiry.objects.filter(pk__in=pks)

        self.admin.mark_as_unread(self._make_request(), qs)

        assert PropertyInquiry.objects.filter(pk__in=pks, is_read=False).count() == 3

    @pytest.mark.django_db
    def test_mark_as_unread_does_not_affect_unselected_inquiries(self):
        selected = PropertyInquiryFactory.create_batch(2, is_read=True)
        unselected = PropertyInquiryFactory(is_read=True)
        qs = PropertyInquiry.objects.filter(pk__in=[i.pk for i in selected])

        self.admin.mark_as_unread(self._make_request(), qs)

        # Unselected inquiry should remain read
        unselected.refresh_from_db()
        assert unselected.is_read is True

    @pytest.mark.django_db
    def test_mark_as_read_on_already_read_inquiries(self):
        inquiries = PropertyInquiryFactory.create_batch(2, is_read=True)
        pks = [i.pk for i in inquiries]
        qs = PropertyInquiry.objects.filter(pk__in=pks)

        # Should not raise and should keep them as read
        self.admin.mark_as_read(self._make_request(), qs)

        assert PropertyInquiry.objects.filter(pk__in=pks, is_read=True).count() == 2

    @pytest.mark.django_db
    def test_mark_as_unread_on_already_unread_inquiries(self):
        inquiries = PropertyInquiryFactory.create_batch(2, is_read=False)
        pks = [i.pk for i in inquiries]
        qs = PropertyInquiry.objects.filter(pk__in=pks)

        # Should not raise and should keep them as unread
        self.admin.mark_as_unread(self._make_request(), qs)

        assert PropertyInquiry.objects.filter(pk__in=pks, is_read=False).count() == 2
