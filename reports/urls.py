
from django.urls import path
from .views import (
    dashboard,
    report_filters,
    summary_report_pdf
)

urlpatterns = [
    path('', dashboard, name='dashboard'),

    path(
        'reports/',
        report_filters,
        name='report_filters'
    ),

    path(
        'reports/pdf/',
        summary_report_pdf,
        name='summary_report_pdf'
    ),
]