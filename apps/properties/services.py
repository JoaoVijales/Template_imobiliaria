from typing import Optional

from django.db.models import QuerySet
from django.http import Http404

from .models import Property, PropertyInquiry
from .repositories import PropertyRepository

# Number of featured properties shown on the homepage
HOMEPAGE_FEATURED_LIMIT = 6
# Number of recent properties shown on the homepage
HOMEPAGE_RECENT_LIMIT = 8


class PropertyService:
    """
    Application-level business logic for properties.

    Depends on PropertyRepository for data access, making it easy to
    swap implementations or inject mocks in tests.
    """

    def __init__(self, repository: Optional[PropertyRepository] = None) -> None:
        self._repo = repository or PropertyRepository()

    def get_homepage_data(self) -> dict:
        """
        Assemble data required to render the homepage.

        Returns a dict with:
            featured  – up to HOMEPAGE_FEATURED_LIMIT featured properties
            recent    – up to HOMEPAGE_RECENT_LIMIT recently added properties
        """
        featured = self._repo.get_featured()[:HOMEPAGE_FEATURED_LIMIT]
        recent = self._repo.get_all_active()[:HOMEPAGE_RECENT_LIMIT]
        return {
            'featured': featured,
            'recent': recent,
        }

    def get_listing(self, filters: dict) -> QuerySet:
        """
        Return a filtered queryset for the property listing page.

        If a free-text query ('q') is present in filters it is applied first;
        remaining filter keys are then applied on top of the search results.
        """
        query = filters.pop('q', None)

        if query:
            qs = self._repo.search(query)
            # Apply remaining filters on top of search results
            if filters:
                qs = self._apply_filters_to_qs(qs, filters)
            return qs

        return self._repo.get_filtered(filters)

    def get_detail(self, slug: str) -> Property:
        """
        Retrieve a single active property by slug.

        Raises Http404 when no active property matches the slug.
        """
        prop = self._repo.get_by_slug(slug)
        if prop is None:
            raise Http404(f'Imóvel com slug "{slug}" não encontrado.')
        return prop

    def get_similar_properties(self, prop: Property, limit: int = 4) -> QuerySet:
        """Return properties similar to the given one."""
        return self._repo.get_similar(prop, limit=limit)

    def record_inquiry(self, property_id: int, form_data: dict) -> PropertyInquiry:
        """
        Persist a new contact inquiry for the given property.

        Args:
            property_id: Primary key of the target Property.
            form_data:   Cleaned data dict from PropertyInquiryForm.

        Returns:
            The newly created PropertyInquiry instance.

        Raises:
            Property.DoesNotExist: When no property matches the given id.
        """
        prop = Property.objects.get(pk=property_id)
        return PropertyInquiry.objects.create(
            property=prop,
            name=form_data['name'],
            email=form_data['email'],
            phone=form_data.get('phone', ''),
            message=form_data['message'],
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_filters_to_qs(self, qs: QuerySet, filters: dict) -> QuerySet:
        """Apply the same filter logic as PropertyRepository.get_filtered to an existing QS."""
        from django.db.models import Q  # local import to avoid circular issues

        listing_type = filters.get('listing_type')
        if listing_type:
            qs = qs.filter(listing_type=listing_type)

        property_type = filters.get('property_type')
        if property_type:
            qs = qs.filter(property_type=property_type)

        city = filters.get('city')
        if city:
            qs = qs.filter(city__icontains=city)

        min_price = filters.get('min_price')
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)

        max_price = filters.get('max_price')
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)

        min_bedrooms = filters.get('min_bedrooms')
        if min_bedrooms is not None:
            qs = qs.filter(bedrooms__gte=min_bedrooms)

        return qs
