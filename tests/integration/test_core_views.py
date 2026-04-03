"""
Integration tests for core views: HomeView, AboutView, ContactView.
Exercises the full Django request/response cycle using the test client.
"""
import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from tests.fixtures.factories import PropertyFactory


@pytest.mark.django_db
class TestHomeView:
    """Tests for the HomeView landing page."""

    def test_should_return_200(self, client):
        response = client.get(reverse('core:home'))
        assert response.status_code == 200

    def test_should_use_correct_template(self, client):
        response = client.get(reverse('core:home'))
        assert 'core/home.html' in [t.name for t in response.templates]

    def test_should_pass_featured_properties_in_context(self, client):
        featured1 = PropertyFactory(is_featured=True, is_active=True)
        featured2 = PropertyFactory(is_featured=True, is_active=True)
        PropertyFactory(is_featured=False, is_active=True)

        response = client.get(reverse('core:home'))

        assert response.status_code == 200
        featured_pks = [p.pk for p in response.context['featured_properties']]
        assert featured1.pk in featured_pks
        assert featured2.pk in featured_pks

    def test_should_pass_recent_properties_in_context(self, client):
        prop = PropertyFactory(is_active=True)

        response = client.get(reverse('core:home'))

        assert response.status_code == 200
        assert 'recent_properties' in response.context
        recent_pks = [p.pk for p in response.context['recent_properties']]
        assert prop.pk in recent_pks

    def test_should_pass_cities_in_context(self, client):
        PropertyFactory(city='Curitiba', is_active=True)
        PropertyFactory(city='São Paulo', is_active=True)

        response = client.get(reverse('core:home'))

        assert response.status_code == 200
        assert 'cities' in response.context
        cities = list(response.context['cities'])
        assert 'Curitiba' in cities
        assert 'São Paulo' in cities

    def test_should_only_show_active_properties_in_recent(self, client):
        active = PropertyFactory(is_active=True)
        inactive = PropertyFactory(is_active=False)

        response = client.get(reverse('core:home'))

        assert response.status_code == 200
        recent_pks = [p.pk for p in response.context['recent_properties']]
        assert active.pk in recent_pks
        assert inactive.pk not in recent_pks

    def test_should_not_show_inactive_as_featured(self, client):
        inactive_featured = PropertyFactory(is_featured=True, is_active=False)

        response = client.get(reverse('core:home'))

        assert response.status_code == 200
        featured_pks = [p.pk for p in response.context['featured_properties']]
        assert inactive_featured.pk not in featured_pks

    def test_should_limit_featured_properties_to_six(self, client):
        PropertyFactory.create_batch(8, is_featured=True, is_active=True)

        response = client.get(reverse('core:home'))

        assert response.status_code == 200
        assert len(list(response.context['featured_properties'])) <= 6

    def test_should_limit_recent_properties_to_eight(self, client):
        PropertyFactory.create_batch(12, is_active=True)

        response = client.get(reverse('core:home'))

        assert response.status_code == 200
        assert len(list(response.context['recent_properties'])) <= 8


@pytest.mark.django_db
class TestAboutView:
    """Tests for the AboutView static page."""

    def test_should_return_200(self, client):
        response = client.get(reverse('core:about'))
        assert response.status_code == 200

    def test_should_use_correct_template(self, client):
        response = client.get(reverse('core:about'))
        assert 'core/about.html' in [t.name for t in response.templates]


@pytest.mark.django_db
class TestContactView:
    """Tests for the ContactView form page."""

    VALID_POST_DATA = {
        'name': 'João Silva',
        'email': 'joao@email.com',
        'phone': '11999999999',
        'subject': 'Interesse em imóvel',
        'message': 'Gostaria de mais informações sobre os imóveis disponíveis.',
    }

    def test_get_should_return_200(self, client):
        response = client.get(reverse('core:contact'))
        assert response.status_code == 200

    def test_get_should_use_correct_template(self, client):
        response = client.get(reverse('core:contact'))
        assert 'core/contact.html' in [t.name for t in response.templates]

    def test_get_should_have_form_in_context(self, client):
        response = client.get(reverse('core:contact'))
        assert 'form' in response.context

    def test_post_valid_should_redirect_to_contact(self, client):
        response = client.post(reverse('core:contact'), self.VALID_POST_DATA)
        assert response.status_code == 302
        assert response['Location'] == reverse('core:contact')

    def test_post_valid_should_show_success_message(self, client):
        response = client.post(
            reverse('core:contact'),
            self.VALID_POST_DATA,
            follow=True,
        )
        assert response.status_code == 200
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'sucesso' in str(messages[0]).lower()

    def test_post_invalid_missing_name_should_return_200_with_errors(self, client):
        data = {**self.VALID_POST_DATA, 'name': ''}
        response = client.post(reverse('core:contact'), data)
        assert response.status_code == 200
        assert response.context['form'].errors
        assert 'name' in response.context['form'].errors

    def test_post_invalid_bad_email_should_show_form_error(self, client):
        data = {**self.VALID_POST_DATA, 'email': 'not-a-valid-email'}
        response = client.post(reverse('core:contact'), data)
        assert response.status_code == 200
        assert 'email' in response.context['form'].errors

    def test_post_invalid_missing_subject_should_return_200_with_errors(self, client):
        data = {**self.VALID_POST_DATA, 'subject': ''}
        response = client.post(reverse('core:contact'), data)
        assert response.status_code == 200
        assert 'subject' in response.context['form'].errors

    def test_post_invalid_missing_message_should_return_200_with_errors(self, client):
        data = {**self.VALID_POST_DATA, 'message': ''}
        response = client.post(reverse('core:contact'), data)
        assert response.status_code == 200
        assert 'message' in response.context['form'].errors

    def test_post_without_optional_phone_should_succeed(self, client):
        data = {k: v for k, v in self.VALID_POST_DATA.items() if k != 'phone'}
        response = client.post(reverse('core:contact'), data)
        # phone is optional, so this should still redirect
        assert response.status_code == 302
