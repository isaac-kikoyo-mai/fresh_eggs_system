from django.shortcuts import render
from django.shortcuts import redirect

from .forms import SaleForm
from .forms import ExpenseForm


def new_sale(request):

    form = SaleForm(
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
        'sales/new_sale.html',
        {'form': form}
    )


def add_expense(request):

    form = ExpenseForm(
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
        'sales/add_expense.html',
        {'form': form}
    )