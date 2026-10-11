from django.shortcuts import render
from django.shortcuts import redirect

from .forms import StockForm


def add_inventory(request):

    form = StockForm(
        request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            form.save()

            return redirect(
                'dashboard'
            )

    return render(
        request,
        'inventory/add_inventory.html',
        {'form': form}
    )
