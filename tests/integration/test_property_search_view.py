"""
Integration tests for PropertySearchView (AJAX/non-AJAX search endpoint).
"""
import json

import pytest
from django.urls import reverse

from tests.fixtures.factories import PropertyFactory


@pytest.mark.django_db
class TestPropertySearchView:
    """Tests for the AJAX-friendly property search endpoint."""

    @property
    def SEARCH_URL(self):
        return reverse('properties:search')

    def test_should_return_200_for_ajax_get_request(self, client):
        response = client.get(
            self.SEARCH_URL,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        assert response.status_code == 200

    def test_should_return_json_for_ajax_request(self, client):
        response = client.get(
            self.SEARCH_URL,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        assert response['Content-Type'] == 'application/json'

    def test_should_return_results_key_in_json_response(self, client):
        response = client.get(
            self.SEARCH_URL,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        data = json.loads(response.content)
        assert 'results' in data

    def test_should_return_matching_property_for_ajax_search(self, client):
        prop = PropertyFactory(title='Casa em Floripa', is_active=True)
        PropertyFactory(title='Apartamento em Recife', is_active=True)

        response = client.get(
            self.SEARCH_URL,
            {'q': 'Floripa'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        result_ids = [r['id'] for r in data['results']]
        assert prop.pk in result_ids

    def test_should_not_return_non_matching_property_for_ajax_search(self, client):
        PropertyFactory(title='Casa em Floripa', is_active=True)
        other = PropertyFactory(title='Apartamento em Recife', is_active=True)

        response = client.get(
            self.SEARCH_URL,
            {'q': 'Floripa'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        data = json.loads(response.content)
        result_ids = [r['id'] for r in data['results']]
        assert other.pk not in result_ids

    def test_ajax_result_contains_required_fields(self, client):
        PropertyFactory(
            title='Cobertura Duplex',
            city='Curitiba',
            is_active=True,
        )

        response = client.get(
            self.SEARCH_URL,
            {'q': 'Cobertura'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        data = json.loads(response.content)
        assert len(data['results']) >= 1
        result = data['results'][0]
        for field in ('id', 'title', 'slug', 'city', 'price', 'listing_type', 'property_type', 'url'):
            assert field in result, f"Field '{field}' missing from result"

    def test_should_redirect_for_non_ajax_request(self, client):
        response = client.get(self.SEARCH_URL, {'q': 'casa'})
        assert response.status_code == 302
        assert '/imoveis/' in response['Location']
        assert 'q=casa' in response['Location']

    def test_non_ajax_redirect_preserves_query_string(self, client):
        response = client.get(self.SEARCH_URL, {'q': 'apartamento'})
        assert response.status_code == 302
        assert 'q=apartamento' in response['Location']

    def test_should_return_empty_results_for_no_match_ajax(self, client):
        PropertyFactory(title='Casa em Porto Alegre', is_active=True)

        response = client.get(
            self.SEARCH_URL,
            {'q': 'zzz-nao-existe-zzz'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        data = json.loads(response.content)
        assert data['results'] == []

    def test_should_not_exceed_max_results_limit(self, client):
        PropertyFactory.create_batch(15, title='Casa em Manaus', is_active=True)

        response = client.get(
            self.SEARCH_URL,
            {'q': 'Manaus'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        data = json.loads(response.content)
        assert len(data['results']) <= 10

    def test_should_not_include_inactive_properties_in_results(self, client):
        inactive = PropertyFactory(title='Casa Inativa Busca', is_active=False)

        response = client.get(
            self.SEARCH_URL,
            {'q': 'Inativa Busca'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        data = json.loads(response.content)
        result_ids = [r['id'] for r in data['results']]
        assert inactive.pk not in result_ids

    def test_should_handle_empty_query_for_ajax_request(self, client):
        PropertyFactory(is_active=True)

        response = client.get(
            self.SEARCH_URL,
            {'q': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'results' in data
