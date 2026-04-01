from django.db import models


class PropertyQuerySet(models.QuerySet):
    """Custom QuerySet providing chainable filter methods for Property."""

    def active(self) -> 'PropertyQuerySet':
        """Return only active properties."""
        return self.filter(is_active=True)

    def featured(self) -> 'PropertyQuerySet':
        """Return featured and active properties."""
        return self.filter(is_featured=True, is_active=True)

    def for_sale(self) -> 'PropertyQuerySet':
        """Return active properties listed for sale."""
        return self.filter(listing_type='sale', is_active=True)

    def for_rent(self) -> 'PropertyQuerySet':
        """Return active properties listed for rent."""
        return self.filter(listing_type='rent', is_active=True)

    def by_city(self, city: str) -> 'PropertyQuerySet':
        """Filter properties by city name (case-insensitive)."""
        return self.filter(city__iexact=city)

    def by_type(self, property_type: str) -> 'PropertyQuerySet':
        """Filter properties by property type."""
        return self.filter(property_type=property_type)

    def with_images(self) -> 'PropertyQuerySet':
        """Prefetch related images to avoid N+1 queries."""
        return self.prefetch_related('images')


class PropertyManager(models.Manager):
    """Custom manager for Property using PropertyQuerySet."""

    def get_queryset(self) -> PropertyQuerySet:
        return PropertyQuerySet(self.model, using=self._db)

    def active(self) -> PropertyQuerySet:
        """Return only active properties."""
        return self.get_queryset().active()

    def featured(self) -> PropertyQuerySet:
        """Return featured and active properties."""
        return self.get_queryset().featured()

    def for_sale(self) -> PropertyQuerySet:
        """Return active properties listed for sale."""
        return self.get_queryset().for_sale()

    def for_rent(self) -> PropertyQuerySet:
        """Return active properties listed for rent."""
        return self.get_queryset().for_rent()

    def by_city(self, city: str) -> PropertyQuerySet:
        """Filter properties by city name (case-insensitive)."""
        return self.get_queryset().by_city(city)

    def by_type(self, property_type: str) -> PropertyQuerySet:
        """Filter properties by property type."""
        return self.get_queryset().by_type(property_type)
