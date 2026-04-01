from typing import Optional

from django.db.models import Q, QuerySet

from .models import Property


class PropertyRepository:
    """
    Data access layer for Property entities.

    Centralises all database queries, keeping views and services
    free from ORM details and making queries easy to test in isolation.
    """

    def get_all_active(self) -> QuerySet:
        """Return all active properties with their images pre-fetched."""
        return (
            Property.objects.active()
            .with_images()
            .select_related()
        )

    def get_featured(self) -> QuerySet:
        """Return featured, active properties (at most 6 for homepage use)."""
        return (
            Property.objects.featured()
            .with_images()
        )

    def get_by_slug(self, slug: str) -> Optional[Property]:
        """
        Retrieve a single active property by its slug.

        Returns None when no matching property is found.
        """
        return (
            Property.objects.active()
            .prefetch_related('images')
            .filter(slug=slug)
            .first()
        )

    def get_filtered(self, filters: dict) -> QuerySet:
        """
        Apply a dictionary of optional filters to the active property queryset.

        Supported keys:
            listing_type (str)  – 'sale' or 'rent'
            property_type (str) – value from PropertyType choices
            city (str)          – case-insensitive city match
            min_price (Decimal) – lower price bound (inclusive)
            max_price (Decimal) – upper price bound (inclusive)
            min_bedrooms (int)  – minimum number of bedrooms
        """
        qs = self.get_all_active()

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

    def search(self, query: str) -> QuerySet:
        """
        Full-text search across title, description, address, city, and neighbourhood.

        Returns active properties matching any of those fields.
        """
        if not query or not query.strip():
            return self.get_all_active()

        return (
            self.get_all_active()
            .filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(address__icontains=query)
                | Q(city__icontains=query)
                | Q(neighborhood__icontains=query)
            )
            .distinct()
        )

    def get_similar(self, prop: Property, limit: int = 4) -> QuerySet:
        """
        Return properties similar to the given one (same type and city),
        excluding the property itself.
        """
        return (
            Property.objects.active()
            .filter(property_type=prop.property_type, city__iexact=prop.city)
            .exclude(pk=prop.pk)
            .with_images()[:limit]
        )
