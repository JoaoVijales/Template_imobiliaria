from django.urls import path

from .views import PropertyDetailView, PropertyListView, PropertySearchView

app_name = 'properties'

urlpatterns = [
    path('imoveis/', PropertyListView.as_view(), name='list'),
    path('imoveis/buscar/', PropertySearchView.as_view(), name='search'),
    path('imoveis/<slug:slug>/', PropertyDetailView.as_view(), name='detail'),
]
