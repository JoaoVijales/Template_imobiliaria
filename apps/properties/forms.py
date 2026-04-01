from django import forms

from .models import ListingType, PropertyInquiry, PropertyType


class PropertySearchForm(forms.Form):
    """Form for filtering the property listing page."""

    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Buscar imóveis…',
                'class': 'form-control',
            }
        ),
    )
    listing_type = forms.ChoiceField(
        required=False,
        label='Comprar / Alugar',
        choices=[('', 'Comprar/Alugar')] + list(ListingType.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    property_type = forms.ChoiceField(
        required=False,
        label='Tipo de Imóvel',
        choices=[('', 'Todos os tipos')] + list(PropertyType.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    city = forms.CharField(
        required=False,
        label='Cidade',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Cidade',
                'class': 'form-control',
            }
        ),
    )
    min_price = forms.DecimalField(
        required=False,
        label='Preço mínimo',
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Preço mínimo',
                'class': 'form-control',
                'step': '1000',
            }
        ),
    )
    max_price = forms.DecimalField(
        required=False,
        label='Preço máximo',
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Preço máximo',
                'class': 'form-control',
                'step': '1000',
            }
        ),
    )
    min_bedrooms = forms.IntegerField(
        required=False,
        label='Mínimo de quartos',
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Quartos',
                'class': 'form-control',
                'min': '0',
            }
        ),
    )

    def get_filters(self) -> dict:
        """
        Return a clean filters dict from validated form data,
        omitting empty / falsy values so they are ignored by the repository.
        """
        data = self.cleaned_data
        filters: dict = {}

        if data.get('q'):
            filters['q'] = data['q'].strip()
        if data.get('listing_type'):
            filters['listing_type'] = data['listing_type']
        if data.get('property_type'):
            filters['property_type'] = data['property_type']
        if data.get('city'):
            filters['city'] = data['city'].strip()
        if data.get('min_price') is not None:
            filters['min_price'] = data['min_price']
        if data.get('max_price') is not None:
            filters['max_price'] = data['max_price']
        if data.get('min_bedrooms') is not None:
            filters['min_bedrooms'] = data['min_bedrooms']

        return filters


class PropertyInquiryForm(forms.ModelForm):
    """Contact form for a visitor to enquire about a specific property."""

    class Meta:
        model = PropertyInquiry
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': 'Seu nome completo', 'class': 'form-control'}
            ),
            'email': forms.EmailInput(
                attrs={'placeholder': 'seu@email.com', 'class': 'form-control'}
            ),
            'phone': forms.TextInput(
                attrs={'placeholder': '(11) 99999-9999', 'class': 'form-control'}
            ),
            'message': forms.Textarea(
                attrs={
                    'placeholder': 'Gostaria de mais informações sobre este imóvel…',
                    'class': 'form-control',
                    'rows': 4,
                }
            ),
        }
        labels = {
            'name': 'Nome',
            'email': 'E-mail',
            'phone': 'Telefone',
            'message': 'Mensagem',
        }
