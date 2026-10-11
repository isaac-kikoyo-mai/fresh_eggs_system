from django import forms
from .models import Stock


class StockForm(forms.ModelForm):

    class Meta:
        model = Stock

        fields = [
            'batch_no',
            'supplier',
            'date_received',
            'trays_received',
            'cost_per_tray'
        ]

        widgets = {
            'date_received': forms.DateInput(
                attrs={'type': 'date'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'form-select'
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control'
                })

            field.widget.attrs.update({
                'placeholder': field.label
            })