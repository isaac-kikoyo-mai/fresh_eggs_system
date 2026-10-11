from django.urls import path

from .views import (
    new_sale,
    add_expense
)

urlpatterns = [

    path(
        'new/',
        new_sale,
        name='new_sale'
    ),

    path(
        'expense/',
        add_expense,
        name='add_expense'
    ),
]