from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.urls import reverse_lazy

from apps.properties.repositories import PropertyRepository
from .forms import ContactForm
from .services import ContactService


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        repo = PropertyRepository()
        context['featured_properties'] = repo.get_featured()[:6]
        context['recent_properties'] = repo.get_all_active()[:8]
        context['cities'] = repo.get_available_cities()
        return context


_TEAM = [
    {'name': 'Ana Costa',      'role': 'Diretora Comercial'},
    {'name': 'Carlos Melo',    'role': 'Corretor Sênior'},
    {'name': 'Beatriz Lima',   'role': 'Especialista Residencial'},
    {'name': 'Rafael Santos',  'role': 'Consultor de Investimentos'},
]


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = _TEAM
        return context


class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')

    def form_valid(self, form):
        ContactService().send_contact(form.cleaned_data)
        messages.success(
            self.request,
            'Mensagem enviada com sucesso! Em breve entraremos em contato.',
        )
        return super().form_valid(form)
