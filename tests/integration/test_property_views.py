"""
Integration tests for PropertyListView and PropertyDetailView.
These tests exercise the full Django request/response cycle using the test client.
"""
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.properties.models import PropertyInquiry
from tests.fixtures.factories import PropertyFactory, PropertyInquiryFactory


# ---------------------------------------------------------------------------
# TestPropertyListView
# ---------------------------------------------------------------------------


class TestPropertyListView:
    """Integration tests for the paginated property listing page."""

    @property
    def LIST_URL(self):
        return reverse('properties:list')

    @pytest.mark.django_db
    def test_should_return_200_status(self, client):
        response = client.get(self.LIST_URL)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_should_use_correct_template(self, client):
        response = client.get(self.LIST_URL)
        assert 'properties/property_list.html' in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_should_display_active_properties_only(self, client):
        active = PropertyFactory(title='Casa Ativa', is_active=True)
        inactive = PropertyFactory(title='Casa Inativa', is_active=False)

        response = client.get(self.LIST_URL)

        assert response.status_code == 200
        properties = list(response.context['properties'])
        pks = [p.pk for p in properties]
        assert active.pk in pks
        assert inactive.pk not in pks

    @pytest.mark.django_db
    def test_should_display_multiple_active_properties(self, client):
        PropertyFactory.create_batch(3, is_active=True)
        PropertyFactory.create_batch(2, is_active=False)

        response = client.get(self.LIST_URL)

        assert response.status_code == 200
        # The page may be paginated, but all 3 active should be in total count
        assert response.context['total_count'] == 3

    @pytest.mark.django_db
    def test_should_filter_by_city_when_provided(self, client):
        sp_prop = PropertyFactory(city='São Paulo', is_active=True)
        rj_prop = PropertyFactory(city='Rio de Janeiro', is_active=True)

        response = client.get(self.LIST_URL, {'city': 'São Paulo'})

        assert response.status_code == 200
        pks = [p.pk for p in response.context['properties']]
        assert sp_prop.pk in pks
        assert rj_prop.pk not in pks

    @pytest.mark.django_db
    def test_should_filter_by_listing_type_sale(self, client):
        sale = PropertyFactory(listing_type='sale', is_active=True)
        rent = PropertyFactory(listing_type='rent', is_active=True)

        response = client.get(self.LIST_URL, {'listing_type': 'sale'})

        assert response.status_code == 200
        pks = [p.pk for p in response.context['properties']]
        assert sale.pk in pks
        assert rent.pk not in pks

    @pytest.mark.django_db
    def test_should_filter_by_listing_type_rent(self, client):
        sale = PropertyFactory(listing_type='sale', is_active=True)
        rent = PropertyFactory(listing_type='rent', is_active=True)

        response = client.get(self.LIST_URL, {'listing_type': 'rent'})

        assert response.status_code == 200
        pks = [p.pk for p in response.context['properties']]
        assert rent.pk in pks
        assert sale.pk not in pks

    @pytest.mark.django_db
    def test_should_filter_by_min_price(self, client):
        cheap = PropertyFactory(price=Decimal('50000.00'), is_active=True)
        expensive = PropertyFactory(price=Decimal('500000.00'), is_active=True)

        response = client.get(self.LIST_URL, {'min_price': '200000'})

        assert response.status_code == 200
        pks = [p.pk for p in response.context['properties']]
        assert expensive.pk in pks
        assert cheap.pk not in pks

    @pytest.mark.django_db
    def test_should_filter_by_max_price(self, client):
        cheap = PropertyFactory(price=Decimal('80000.00'), is_active=True)
        expensive = PropertyFactory(price=Decimal('900000.00'), is_active=True)

        response = client.get(self.LIST_URL, {'max_price': '200000'})

        assert response.status_code == 200
        pks = [p.pk for p in response.context['properties']]
        assert cheap.pk in pks
        assert expensive.pk not in pks

    @pytest.mark.django_db
    def test_should_show_empty_state_when_no_results(self, client):
        # No properties created → empty queryset
        response = client.get(self.LIST_URL)

        assert response.status_code == 200
        assert len(list(response.context['properties'])) == 0
        assert response.context['total_count'] == 0

    @pytest.mark.django_db
    def test_should_show_empty_state_when_filter_matches_nothing(self, client):
        PropertyFactory(city='Curitiba', is_active=True)

        response = client.get(self.LIST_URL, {'city': 'Manaus'})

        assert response.status_code == 200
        assert len(list(response.context['properties'])) == 0

    @pytest.mark.django_db
    def test_should_include_search_form_in_context(self, client):
        response = client.get(self.LIST_URL)
        assert 'search_form' in response.context

    @pytest.mark.django_db
    def test_should_include_total_count_in_context(self, client):
        PropertyFactory.create_batch(5, is_active=True)
        response = client.get(self.LIST_URL)
        assert 'total_count' in response.context
        assert response.context['total_count'] == 5

    @pytest.mark.django_db
    def test_should_search_by_query_parameter(self, client):
        matching = PropertyFactory(title='Cobertura Duplex Exclusiva', is_active=True)
        unrelated = PropertyFactory(title='Casa Simples', is_active=True)

        response = client.get(self.LIST_URL, {'q': 'Cobertura'})

        assert response.status_code == 200
        pks = [p.pk for p in response.context['properties']]
        assert matching.pk in pks
        assert unrelated.pk not in pks


# ---------------------------------------------------------------------------
# TestPropertyDetailView
# ---------------------------------------------------------------------------


class TestPropertyDetailView:
    """Integration tests for the property detail page, including the inquiry form."""

    @pytest.mark.django_db
    def test_should_return_200_for_existing_property(self, client):
        prop = PropertyFactory(slug='casa-em-sp-1234', is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})

        response = client.get(url)

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_should_use_correct_template(self, client):
        prop = PropertyFactory(is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})

        response = client.get(url)

        assert 'properties/property_detail.html' in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_should_return_404_for_nonexistent_slug(self, client):
        response = client.get('/imoveis/slug-que-nao-existe/')
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_should_return_404_for_inactive_property(self, client):
        prop = PropertyFactory(is_active=False)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})

        response = client.get(url)

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_should_show_property_details_in_context(self, client):
        prop = PropertyFactory(
            title='Apartamento Premium',
            city='São Paulo',
            is_active=True,
        )
        url = reverse('properties:detail', kwargs={'slug': prop.slug})

        response = client.get(url)

        assert response.status_code == 200
        assert response.context['property'].pk == prop.pk
        assert response.context['property'].title == 'Apartamento Premium'

    @pytest.mark.django_db
    def test_should_render_property_title_in_response_body(self, client):
        prop = PropertyFactory(title='Penthouse Vista Mar', is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})

        response = client.get(url)

        assert b'Penthouse Vista Mar' in response.content

    @pytest.mark.django_db
    def test_should_include_inquiry_form_in_context(self, client):
        prop = PropertyFactory(is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})

        response = client.get(url)

        assert 'inquiry_form' in response.context

    @pytest.mark.django_db
    def test_should_include_similar_properties_in_context(self, client):
        prop = PropertyFactory(is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})

        response = client.get(url)

        assert 'similar_properties' in response.context

    @pytest.mark.django_db
    def test_should_create_inquiry_on_valid_post(self, client):
        prop = PropertyFactory(is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})
        post_data = {
            'name': 'Fernanda Costa',
            'email': 'fernanda@example.com',
            'phone': '(41) 91234-5678',
            'message': 'Gostaria de visitar o imóvel na próxima semana.',
        }

        assert PropertyInquiry.objects.filter(property=prop).count() == 0

        response = client.post(url, post_data, follow=True)

        assert response.status_code == 200
        assert PropertyInquiry.objects.filter(property=prop).count() == 1

        inquiry = PropertyInquiry.objects.get(property=prop)
        assert inquiry.name == 'Fernanda Costa'
        assert inquiry.email == 'fernanda@example.com'
        assert inquiry.phone == '(41) 91234-5678'
        assert inquiry.message == 'Gostaria de visitar o imóvel na próxima semana.'

    @pytest.mark.django_db
    def test_should_redirect_to_detail_page_after_valid_inquiry_post(self, client):
        prop = PropertyFactory(is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})
        post_data = {
            'name': 'Ricardo Alves',
            'email': 'ricardo@example.com',
            'message': 'Preciso de informações sobre o financiamento.',
        }

        response = client.post(url, post_data)

        assert response.status_code == 302
        assert response['Location'] == url

    @pytest.mark.django_db
    def test_should_not_create_inquiry_on_invalid_post_missing_name(self, client):
        prop = PropertyFactory(is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})
        post_data = {
            # name is missing
            'email': 'test@example.com',
            'message': 'Mensagem de teste.',
        }

        response = client.post(url, post_data)

        assert response.status_code == 200  # re-renders the form with errors
        assert PropertyInquiry.objects.filter(property=prop).count() == 0

    @pytest.mark.django_db
    def test_should_not_create_inquiry_on_invalid_post_bad_email(self, client):
        prop = PropertyFactory(is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})
        post_data = {
            'name': 'Test User',
            'email': 'not-valid-email',
            'message': 'Mensagem de teste.',
        }

        response = client.post(url, post_data)

        assert response.status_code == 200
        assert PropertyInquiry.objects.filter(property=prop).count() == 0

    @pytest.mark.django_db
    def test_should_not_create_inquiry_on_invalid_post_missing_message(self, client):
        prop = PropertyFactory(is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})
        post_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            # message is missing
        }

        response = client.post(url, post_data)

        assert response.status_code == 200
        assert PropertyInquiry.objects.filter(property=prop).count() == 0

    @pytest.mark.django_db
    def test_should_show_form_errors_when_inquiry_post_is_invalid(self, client):
        prop = PropertyFactory(is_active=True)
        url = reverse('properties:detail', kwargs={'slug': prop.slug})
        post_data = {
            'name': '',
            'email': 'bad',
            'message': '',
        }

        response = client.post(url, post_data)

        assert response.status_code == 200
        form = response.context['inquiry_form']
        assert form.errors  # form should have errors
