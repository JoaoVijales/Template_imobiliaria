from decimal import Decimal
from typing import Optional

from django.db import models
from django.urls import reverse

from .managers import PropertyManager


class PropertyType(models.TextChoices):
    APARTMENT = 'apartment', 'Apartamento'
    HOUSE = 'house', 'Casa'
    COMMERCIAL = 'commercial', 'Comercial'
    LAND = 'land', 'Terreno'
    RURAL = 'rural', 'Rural'


class ListingType(models.TextChoices):
    SALE = 'sale', 'Venda'
    RENT = 'rent', 'Aluguel'


class Property(models.Model):
    """Represents a real estate property listing."""

    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Descrição')
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        verbose_name='Tipo de Imóvel',
    )
    listing_type = models.CharField(
        max_length=10,
        choices=ListingType.choices,
        default=ListingType.SALE,
        verbose_name='Tipo de Anúncio',
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Preço',
    )
    area = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text='Área em m²',
        verbose_name='Área (m²)',
    )
    bedrooms = models.PositiveSmallIntegerField(default=0, verbose_name='Quartos')
    bathrooms = models.PositiveSmallIntegerField(default=0, verbose_name='Banheiros')
    parking_spots = models.PositiveSmallIntegerField(default=0, verbose_name='Vagas')
    address = models.CharField(max_length=300, verbose_name='Endereço')
    city = models.CharField(max_length=100, verbose_name='Cidade')
    state = models.CharField(max_length=2, verbose_name='Estado')
    neighborhood = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Bairro',
    )
    zipcode = models.CharField(
        max_length=9,
        blank=True,
        verbose_name='CEP',
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Latitude',
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Longitude',
    )
    is_featured = models.BooleanField(default=False, verbose_name='Destaque')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    objects = PropertyManager()

    class Meta:
        verbose_name = 'Imóvel'
        verbose_name_plural = 'Imóveis'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """Return the canonical URL for this property."""
        return reverse('properties:detail', kwargs={'slug': self.slug})

    @property
    def price_per_sqm(self) -> Optional[Decimal]:
        """Calculate price per square meter. Returns None if area is zero."""
        if self.area and self.area > 0:
            return self.price / self.area
        return None

    @property
    def main_image(self) -> Optional['PropertyImage']:
        """Return the primary image, preferring is_main=True, else first by order."""
        images = self.images.all()
        main = images.filter(is_main=True).first()
        if main:
            return main
        return images.first()


class PropertyImage(models.Model):
    """An image associated with a property listing."""

    property = models.ForeignKey(
        Property,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name='Imóvel',
    )
    image = models.ImageField(
        upload_to='properties/%Y/%m/',
        verbose_name='Imagem',
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Legenda',
    )
    is_main = models.BooleanField(default=False, verbose_name='Imagem Principal')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Ordem')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Imagem'
        verbose_name_plural = 'Imagens'

    def __str__(self) -> str:
        return f'Imagem de {self.property.title} (ordem {self.order})'


class PropertyInquiry(models.Model):
    """A contact inquiry submitted by a visitor for a specific property."""

    property = models.ForeignKey(
        Property,
        related_name='inquiries',
        on_delete=models.CASCADE,
        verbose_name='Imóvel',
    )
    name = models.CharField(max_length=100, verbose_name='Nome')
    email = models.EmailField(verbose_name='E-mail')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    message = models.TextField(verbose_name='Mensagem')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Recebido em')
    is_read = models.BooleanField(default=False, verbose_name='Lido')

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Contato de {self.name} — {self.property.title}'
