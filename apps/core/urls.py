from django.urls import path

from .views import AboutView, ContactView, HomeView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('sobre/', AboutView.as_view(), name='about'),
    path('contato/', ContactView.as_view(), name='contact'),
]
