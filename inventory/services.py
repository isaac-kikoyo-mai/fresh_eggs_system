from .models import Stock


def total_stock():

    return sum(
        stock.trays_remaining
        for stock in Stock.objects.all()
    )
