"""
Unit tests for PropertyRepository — verifies the data-access layer in isolation.
"""
from decimal import Decimal

import pytest
from django.http import Http404

from apps.properties.repositories import PropertyRepository
from tests.fixtures.factories import PropertyFactory


@pytest.fixture
def repo():
    return PropertyRepository()


class TestPropertyRepository:
    """Tests for every public method on PropertyRepository."""

    # ------------------------------------------------------------------
    # get_all_active
    # ------------------------------------------------------------------

    @pytest.mark.django_db
    def test_get_all_active_excludes_inactive(self, repo):
        active = PropertyFactory(is_active=True)
        inactive = PropertyFactory(is_active=False)

        result_pks = list(repo.get_all_active().values_list('pk', flat=True))

        assert active.pk in result_pks
        assert inactive.pk not in result_pks

    @pytest.mark.django_db
    def test_get_all_active_returns_all_active_when_multiple_exist(self, repo):
        PropertyFactory.create_batch(4, is_active=True)
        PropertyFactory.create_batch(2, is_active=False)

        assert repo.get_all_active().count() == 4

    # ------------------------------------------------------------------
    # get_featured
    # ------------------------------------------------------------------

    @pytest.mark.django_db
    def test_get_featured_returns_only_featured_active(self, repo):
        featured_active = PropertyFactory(is_featured=True, is_active=True)
        featured_inactive = PropertyFactory(is_featured=True, is_active=False)
        not_featured = PropertyFactory(is_featured=False, is_active=True)

        result_pks = list(repo.get_featured().values_list('pk', flat=True))

        assert featured_active.pk in result_pks
        assert featured_inactive.pk not in result_pks
        assert not_featured.pk not in result_pks

    @pytest.mark.django_db
    def test_get_featured_returns_empty_when_none_exist(self, repo):
        PropertyFactory.create_batch(3, is_featured=False, is_active=True)
        assert repo.get_featured().count() == 0

    # ------------------------------------------------------------------
    # get_by_slug
    # ------------------------------------------------------------------

    @pytest.mark.django_db
    def test_get_by_slug_returns_correct_property(self, repo):
        prop = PropertyFactory(slug='unique-slug-1234', is_active=True)
        PropertyFactory(slug='other-slug-5678', is_active=True)

        result = repo.get_by_slug('unique-slug-1234')

        assert result is not None
        assert result.pk == prop.pk

    @pytest.mark.django_db
    def test_get_by_slug_returns_none_when_property_does_not_exist(self, repo):
        result = repo.get_by_slug('nonexistent-slug-0000')
        assert result is None

    @pytest.mark.django_db
    def test_get_by_slug_returns_none_for_inactive_property(self, repo):
        PropertyFactory(slug='inactive-slug-9999', is_active=False)
        result = repo.get_by_slug('inactive-slug-9999')
        assert result is None

    # ------------------------------------------------------------------
    # get_filtered
    # ------------------------------------------------------------------

    @pytest.mark.django_db
    def test_get_filtered_by_city(self, repo):
        sp = PropertyFactory(city='São Paulo', is_active=True)
        rj = PropertyFactory(city='Rio de Janeiro', is_active=True)

        result_pks = list(repo.get_filtered({'city': 'São Paulo'}).values_list('pk', flat=True))

        assert sp.pk in result_pks
        assert rj.pk not in result_pks

    @pytest.mark.django_db
    def test_get_filtered_by_city_is_case_insensitive(self, repo):
        sp = PropertyFactory(city='São Paulo', is_active=True)

        result_pks = list(repo.get_filtered({'city': 'são paulo'}).values_list('pk', flat=True))

        assert sp.pk in result_pks

    @pytest.mark.django_db
    def test_get_filtered_by_listing_type_sale(self, repo):
        sale = PropertyFactory(listing_type='sale', is_active=True)
        rent = PropertyFactory(listing_type='rent', is_active=True)

        result_pks = list(repo.get_filtered({'listing_type': 'sale'}).values_list('pk', flat=True))

        assert sale.pk in result_pks
        assert rent.pk not in result_pks

    @pytest.mark.django_db
    def test_get_filtered_by_listing_type_rent(self, repo):
        sale = PropertyFactory(listing_type='sale', is_active=True)
        rent = PropertyFactory(listing_type='rent', is_active=True)

        result_pks = list(repo.get_filtered({'listing_type': 'rent'}).values_list('pk', flat=True))

        assert rent.pk in result_pks
        assert sale.pk not in result_pks

    @pytest.mark.django_db
    def test_get_filtered_by_price_range_min_price(self, repo):
        cheap = PropertyFactory(price=Decimal('50000.00'), is_active=True)
        expensive = PropertyFactory(price=Decimal('500000.00'), is_active=True)

        result_pks = list(
            repo.get_filtered({'min_price': Decimal('100000.00')}).values_list('pk', flat=True)
        )

        assert expensive.pk in result_pks
        assert cheap.pk not in result_pks

    @pytest.mark.django_db
    def test_get_filtered_by_price_range_max_price(self, repo):
        cheap = PropertyFactory(price=Decimal('80000.00'), is_active=True)
        expensive = PropertyFactory(price=Decimal('900000.00'), is_active=True)

        result_pks = list(
            repo.get_filtered({'max_price': Decimal('200000.00')}).values_list('pk', flat=True)
        )

        assert cheap.pk in result_pks
        assert expensive.pk not in result_pks

    @pytest.mark.django_db
    def test_get_filtered_by_price_range_inclusive_bounds(self, repo):
        boundary = PropertyFactory(price=Decimal('300000.00'), is_active=True)

        result_pks = list(
            repo.get_filtered({
                'min_price': Decimal('300000.00'),
                'max_price': Decimal('300000.00'),
            }).values_list('pk', flat=True)
        )

        assert boundary.pk in result_pks

    @pytest.mark.django_db
    def test_get_filtered_by_min_bedrooms(self, repo):
        small = PropertyFactory(bedrooms=1, is_active=True)
        large = PropertyFactory(bedrooms=4, is_active=True)

        result_pks = list(
            repo.get_filtered({'min_bedrooms': 3}).values_list('pk', flat=True)
        )

        assert large.pk in result_pks
        assert small.pk not in result_pks

    @pytest.mark.django_db
    def test_get_filtered_combines_multiple_filters(self, repo):
        match = PropertyFactory(
            city='Curitiba', listing_type='sale',
            price=Decimal('250000.00'), bedrooms=3, is_active=True,
        )
        wrong_city = PropertyFactory(
            city='Florianópolis', listing_type='sale',
            price=Decimal('250000.00'), bedrooms=3, is_active=True,
        )

        result_pks = list(
            repo.get_filtered({
                'city': 'Curitiba',
                'listing_type': 'sale',
                'min_price': Decimal('200000.00'),
                'min_bedrooms': 2,
            }).values_list('pk', flat=True)
        )

        assert match.pk in result_pks
        assert wrong_city.pk not in result_pks

    @pytest.mark.django_db
    def test_get_filtered_returns_all_active_when_no_filters(self, repo):
        PropertyFactory.create_batch(3, is_active=True)
        PropertyFactory.create_batch(2, is_active=False)

        assert repo.get_filtered({}).count() == 3

    # ------------------------------------------------------------------
    # search
    # ------------------------------------------------------------------

    @pytest.mark.django_db
    def test_search_finds_by_title(self, repo):
        matching = PropertyFactory(
            title='Cobertura duplex exclusiva', is_active=True
        )
        unrelated = PropertyFactory(title='Casa simples no interior', is_active=True)

        result_pks = list(repo.search('cobertura duplex').values_list('pk', flat=True))

        assert matching.pk in result_pks
        assert unrelated.pk not in result_pks

    @pytest.mark.django_db
    def test_search_finds_by_city(self, repo):
        matching = PropertyFactory(city='Blumenau', is_active=True)
        unrelated = PropertyFactory(city='Campinas', is_active=True)

        result_pks = list(repo.search('Blumenau').values_list('pk', flat=True))

        assert matching.pk in result_pks
        assert unrelated.pk not in result_pks

    @pytest.mark.django_db
    def test_search_finds_by_neighborhood(self, repo):
        matching = PropertyFactory(neighborhood='Bairro Alto', is_active=True)
        unrelated = PropertyFactory(neighborhood='Centro Histórico', is_active=True)

        result_pks = list(repo.search('Bairro Alto').values_list('pk', flat=True))

        assert matching.pk in result_pks
        assert unrelated.pk not in result_pks

    @pytest.mark.django_db
    def test_search_excludes_inactive_properties(self, repo):
        inactive = PropertyFactory(title='Búngalo especial', is_active=False)

        result_pks = list(repo.search('Búngalo especial').values_list('pk', flat=True))

        assert inactive.pk not in result_pks

    @pytest.mark.django_db
    def test_search_with_empty_query_returns_all_active(self, repo):
        PropertyFactory.create_batch(3, is_active=True)
        PropertyFactory.create_batch(2, is_active=False)

        assert repo.search('').count() == 3

    @pytest.mark.django_db
    def test_search_with_whitespace_only_returns_all_active(self, repo):
        PropertyFactory.create_batch(2, is_active=True)

        assert repo.search('   ').count() == 2

    # ------------------------------------------------------------------
    # get_available_cities (via get_all_active distinct cities)
    # ------------------------------------------------------------------

    @pytest.mark.django_db
    def test_get_available_cities_returns_distinct_cities(self, repo):
        PropertyFactory.create_batch(2, city='Salvador', is_active=True)
        PropertyFactory.create_batch(3, city='Recife', is_active=True)
        PropertyFactory(city='Fortaleza', is_active=True)
        PropertyFactory(city='Fortaleza', is_active=False)  # inactive — should not count

        cities = list(
            repo.get_all_active()
            .values_list('city', flat=True)
            .distinct()
            .order_by('city')
        )

        assert cities.count('Salvador') == 1
        assert cities.count('Recife') == 1
        assert cities.count('Fortaleza') == 1
        assert len(cities) == 3
