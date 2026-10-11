from django.contrib import admin
from .models import (
    Customer,
    Sale,
    Expense
)

admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(Expense)