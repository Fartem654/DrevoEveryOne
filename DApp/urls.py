"""Определяет схемы URL для DApp."""

from django.urls import path
from .views import index, family_graph_json

app_name = 'DApp'
urlpatterns = [
    # Домашняя страница
    path('', index, name='index'),
    path('api/family-graph/', family_graph_json, name='family_graph_json'),
]
