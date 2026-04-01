from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import PropertyInquiryForm, PropertySearchForm
from .models import Property
from .services import PropertyService

_service = PropertyService()


class PropertyListView(ListView):
    """
    Paginated listing of properties with optional filtering.

    GET parameters are mapped to PropertySearchForm; valid filters are
    forwarded to PropertyService.get_listing().
    """

    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_queryset(self):
        self._search_form = PropertySearchForm(self.request.GET or None)

        if self._search_form.is_valid():
            filters = self._search_form.get_filters()
            return _service.get_listing(filters)

        return _service.get_listing({})

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['search_form'] = self._search_form
        context['total_count'] = self.get_queryset().count()
        return context


class PropertyDetailView(DetailView):
    """
    Detail page for a single property.

    Also handles POST requests for the contact / inquiry form.
    """

    template_name = 'properties/property_detail.html'
    context_object_name = 'property'

    def get_object(self, queryset=None) -> Property:
        return _service.get_detail(self.kwargs['slug'])

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        prop = context['property']
        context['inquiry_form'] = kwargs.get('inquiry_form', PropertyInquiryForm())
        context['similar_properties'] = _service.get_similar_properties(prop)
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        prop = self.get_object()
        form = PropertyInquiryForm(request.POST)

        if form.is_valid():
            _service.record_inquiry(
                property_id=prop.pk,
                form_data=form.cleaned_data,
            )
            messages.success(
                request,
                'Mensagem enviada com sucesso! Entraremos em contato em breve.',
            )
            return redirect('properties:detail', slug=prop.slug)

        # Re-render the page with form errors intact
        self.object = prop
        context = self.get_context_data(inquiry_form=form)
        return self.render_to_response(context)


class PropertySearchView(View):
    """
    AJAX-friendly endpoint for live property search.

    Accepts GET with a 'q' parameter and returns a JSON list of
    matching active properties (id, title, slug, city, price).
    Falls back to full HTML listing page for non-AJAX requests.
    """

    MAX_RESULTS = 10

    def get(self, request: HttpRequest) -> HttpResponse:
        query = request.GET.get('q', '').strip()
        properties = _service.get_listing({'q': query})[: self.MAX_RESULTS]

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = [
                {
                    'id': p.pk,
                    'title': p.title,
                    'slug': p.slug,
                    'city': p.city,
                    'price': str(p.price),
                    'listing_type': p.get_listing_type_display(),
                    'property_type': p.get_property_type_display(),
                    'url': p.get_absolute_url(),
                }
                for p in properties
            ]
            return JsonResponse({'results': data})

        # Non-AJAX: redirect to the list page preserving the query string
        return redirect(f'/imoveis/?q={query}')
