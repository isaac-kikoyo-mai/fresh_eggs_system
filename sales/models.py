from django.db import models
from django.core.exceptions import ValidationError

from inventory.models import Stock


class Customer(models.Model):

    name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return self.name


class Expense(models.Model):

    date = models.DateField()

    description = models.CharField(
        max_length=200
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return self.description


class Sale(models.Model):

    SALE_TYPES = [
        ('tray', 'Tray'),
        ('piece', 'Piece'),
    ]

    date = models.DateField()

    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    sale_type = models.CharField(
        max_length=10,
        choices=SALE_TYPES
    )

    quantity = models.PositiveIntegerField()

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def revenue(self):
        return (
            self.quantity *
            self.selling_price
        )

    @property
    def cost(self):

        if self.sale_type == 'tray':

            return (
                self.quantity *
                self.stock.cost_per_tray
            )

        cost_per_piece = (
            self.stock.cost_per_tray / 30
        )

        return (
            self.quantity *
            cost_per_piece
        )

    @property
    def profit(self):

        return (
            self.revenue -
            self.cost
        )

    def save(self, *args, **kwargs):

        if not self.pk:

            if self.sale_type == 'tray':

                eggs_to_deduct = (
                    self.quantity * 30
                )

            else:

                eggs_to_deduct = (
                    self.quantity
                )

            if (
                self.stock.eggs_remaining
                < eggs_to_deduct
            ):

                raise ValidationError(
                    "Insufficient stock available."
                )

            self.stock.eggs_remaining -= (
                eggs_to_deduct
            )

            self.stock.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale #{self.id}"