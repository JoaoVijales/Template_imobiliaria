from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Nome completo',
        widget=forms.TextInput(attrs={
            'placeholder': 'Seu nome completo',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition',
        }),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'seu@email.com',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition',
        }),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Telefone',
        widget=forms.TextInput(attrs={
            'placeholder': '(11) 99999-9999',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition',
        }),
    )
    subject = forms.CharField(
        max_length=200,
        label='Assunto',
        widget=forms.TextInput(attrs={
            'placeholder': 'Como podemos ajudar?',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition',
        }),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': 'Descreva sua mensagem...',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition resize-none',
        }),
        label='Mensagem',
    )
