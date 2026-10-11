from django.urls import path

from .views import add_inventory

urlpatterns = [
    path(
        'add/',
        add_inventory,
        name='add_inventory'
    ),
]
