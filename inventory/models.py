from django.db import models


class Stock(models.Model):

    batch_no = models.CharField(
        max_length=50,
        unique=True
    )

    supplier = models.CharField(
        max_length=100
    )

    date_received = models.DateField()

    trays_received = models.PositiveIntegerField()

    eggs_received = models.PositiveIntegerField(
        editable=False,
        default=0
    )

    eggs_remaining = models.PositiveIntegerField(
        editable=False,
        default=0
    )

    cost_per_tray = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.pk:
            self.eggs_received = (
                self.trays_received * 30
            )

            self.eggs_remaining = (
                self.trays_received * 30
            )

        super().save(*args, **kwargs)

    @property
    def trays_remaining(self):
        return round(
            self.eggs_remaining / 30,
            2
        )

    def __str__(self):
        return (
            f"{self.batch_no}"
            f" ({self.trays_remaining} trays)"
        )