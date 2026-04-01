from django.contrib import admin
from django.utils.html import format_html

from .models import Property, PropertyImage, PropertyInquiry


class PropertyImageInline(admin.TabularInline):
    """Inline editor for property images inside the Property admin."""

    model = PropertyImage
    extra = 3
    fields = ['image', 'caption', 'is_main', 'order']
    ordering = ['order', 'id']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Admin interface for Property with grouped fieldsets and inline images."""

    list_display = [
        'title',
        'property_type',
        'listing_type',
        'formatted_price',
        'city',
        'state',
        'is_featured',
        'is_active',
        'created_at',
    ]
    list_filter = [
        'property_type',
        'listing_type',
        'city',
        'state',
        'is_featured',
        'is_active',
    ]
    search_fields = ['title', 'address', 'city', 'neighborhood', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PropertyImageInline]
    list_editable = ['is_featured', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    save_on_top = True

    fieldsets = (
        (
            'Identificação',
            {
                'fields': ('title', 'slug', 'description'),
            },
        ),
        (
            'Classificação',
            {
                'fields': (
                    'property_type',
                    'listing_type',
                    'price',
                    'area',
                ),
            },
        ),
        (
            'Características',
            {
                'fields': ('bedrooms', 'bathrooms', 'parking_spots'),
                'classes': ('collapse',),
            },
        ),
        (
            'Localização',
            {
                'fields': (
                    'address',
                    'neighborhood',
                    'city',
                    'state',
                    'zipcode',
                    'latitude',
                    'longitude',
                ),
            },
        ),
        (
            'Configurações',
            {
                'fields': ('is_featured', 'is_active'),
            },
        ),
        (
            'Auditoria',
            {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',),
            },
        ),
    )

    @admin.display(description='Preço', ordering='price')
    def formatted_price(self, obj: Property) -> str:
        """Display price formatted as Brazilian currency."""
        return format_html(
            'R$ {:,.2f}'.format(obj.price).replace(',', 'X').replace('.', ',').replace('X', '.')
        )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Admin interface for PropertyImage."""

    list_display = ['property', 'caption', 'is_main', 'order']
    list_filter = ['is_main']
    search_fields = ['property__title', 'caption']
    ordering = ['property', 'order']


@admin.register(PropertyInquiry)
class PropertyInquiryAdmin(admin.ModelAdmin):
    """Admin interface for PropertyInquiry with a bulk mark-as-read action."""

    list_display = [
        'name',
        'email',
        'phone',
        'property',
        'created_at',
        'is_read',
    ]
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'property__title', 'message']
    readonly_fields = ['property', 'name', 'email', 'phone', 'message', 'created_at']
    actions = ['mark_as_read', 'mark_as_unread']
    date_hierarchy = 'created_at'

    fieldsets = (
        (
            'Remetente',
            {
                'fields': ('name', 'email', 'phone'),
            },
        ),
        (
            'Imóvel',
            {
                'fields': ('property',),
            },
        ),
        (
            'Mensagem',
            {
                'fields': ('message', 'created_at', 'is_read'),
            },
        ),
    )

    @admin.action(description='Marcar selecionados como lidos')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} contato(s) marcado(s) como lido(s).')

    @admin.action(description='Marcar selecionados como não lidos')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} contato(s) marcado(s) como não lido(s).')
