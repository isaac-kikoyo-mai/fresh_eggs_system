from django import forms

from .models import Sale
from .models import Expense


class SaleForm(forms.ModelForm):

    class Meta:

        model = Sale

        fields = [
            'date',
            'stock',
            'customer',
            'sale_type',
            'quantity',
            'selling_price'
        ]

        widgets = {

            'date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'stock': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'customer': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'sale_type': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'selling_price': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }


class ExpenseForm(forms.ModelForm):

    class Meta:

        model = Expense

        fields = [
            'date',
            'description',
            'amount'
        ]

        widgets = {

            'date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'description': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'amount': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }