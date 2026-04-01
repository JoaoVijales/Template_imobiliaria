"""
Shared pytest fixtures available to all test modules.
"""
import pytest

from tests.fixtures.factories import PropertyFactory, PropertyInquiryFactory


@pytest.fixture
def active_property(db):
    """A single active (non-featured) property."""
    return PropertyFactory(is_active=True, is_featured=False)


@pytest.fixture
def featured_property(db):
    """A single property that is both active and featured."""
    return PropertyFactory(is_featured=True, is_active=True)


@pytest.fixture
def inactive_property(db):
    """A single property that has been deactivated."""
    return PropertyFactory(is_active=False)


@pytest.fixture
def sale_property(db):
    """An active property listed for sale."""
    return PropertyFactory(is_active=True, listing_type='sale')


@pytest.fixture
def rent_property(db):
    """An active property listed for rent."""
    return PropertyFactory(is_active=True, listing_type='rent')


@pytest.fixture
def inquiry_for_active_property(db, active_property):
    """A PropertyInquiry linked to the active_property fixture."""
    return PropertyInquiryFactory(property=active_property)
