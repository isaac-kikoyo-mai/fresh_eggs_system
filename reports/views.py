import pandas as pd
from datetime import datetime

from django.shortcuts import render
from django.db.models import (
    Sum,
    F,
    DecimalField,
    Case,
    When,
    IntegerField
)
from django.db.models.functions import Cast

from inventory.models import Stock
from sales.models import Sale, Expense

from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    Paragraph
)
from reportlab.lib.styles import getSampleStyleSheet


from .forms import ReportFilterForm


def report_filters(request):

    form = ReportFilterForm()

    return render(
        request,
        'reports/report_filters.html',
        {'form': form}
    )

def dashboard(request):

    # ==========================
    # SALES DATA
    # ==========================

    sales = Sale.objects.all().values(
        'date',
        'quantity',
        'selling_price',
        'sale_type',
        'customer__name',
        'stock__cost_per_tray'
    )

    df = pd.DataFrame(sales)

    total_sales = 0
    total_profit = 0

    daily_labels = []
    daily_values = []

    monthly_labels = []
    monthly_sales_values = []
    monthly_profit_values = []

    if not df.empty:

        df['date'] = pd.to_datetime(df['date'])

        # ==========================
        # REVENUE
        # ==========================

        df['revenue'] = (
            df['quantity']
            * df['selling_price']
        )

        # ==========================
        # PROFIT
        # ==========================

        def calculate_profit(row):

            if row['sale_type'] == 'tray':

                cost = (
                    row['quantity']
                    * row['stock__cost_per_tray']
                )

            else:

                cost_per_piece = (
                    row['stock__cost_per_tray'] / 30
                )

                cost = (
                    row['quantity']
                    * cost_per_piece
                )

            return row['revenue'] - cost

        df['profit'] = df.apply(
            calculate_profit,
            axis=1
        )

        total_sales = float(
            df['revenue'].sum()
        )

        total_profit = float(
            df['profit'].sum()
        )

        # ==========================
        # DAILY REVENUE CHART
        # ==========================

        daily_sales = (
            df.groupby('date')['revenue']
            .sum()
            .reset_index()
        )

        daily_labels = (
            daily_sales['date']
            .dt.strftime('%Y-%m-%d')
            .tolist()
        )

        daily_values = (
            daily_sales['revenue']
            .tolist()
        )

        # ==========================
        # MONTHLY CHARTS
        # ==========================

        monthly = (
            df.groupby(
                df['date'].dt.to_period('M')
            )
            .agg(
                revenue=('revenue', 'sum'),
                profit=('profit', 'sum')
            )
            .reset_index()
        )

        monthly_labels = (
            monthly['date']
            .astype(str)
            .tolist()
        )

        monthly_sales_values = (
            monthly['revenue']
            .tolist()
        )

        monthly_profit_values = (
            monthly['profit']
            .tolist()
        )

    # ==========================
    # INVENTORY
    # ==========================

    total_eggs = sum(
        stock.eggs_remaining
        for stock in Stock.objects.all()
    )

    total_stock = round(
        total_eggs / 30,
        2
    )

    # ==========================
    # EXPENSES
    # ==========================

    total_expenses = sum(
        float(expense.amount)
        for expense in Expense.objects.all()
    )

    net_profit = (
        total_profit - total_expenses
    )

    # ==========================
    # LOW STOCK ALERTS
    # ==========================

    low_stock = Stock.objects.filter(
        eggs_remaining__lt=600
    )

    # ==========================
    # TOP CUSTOMERS
    # ==========================

    top_customers = (
        Sale.objects
        .values('customer__name')
        .annotate(

            trays_bought=Sum(
                Case(
                    When(
                        sale_type='tray',
                        then='quantity'
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            ),

            eggs_bought=Sum(
                Case(
                    When(
                        sale_type='piece',
                        then='quantity'
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            ),

            total_revenue=Sum(
                F('quantity') *
                Cast(
                    'selling_price',
                    DecimalField(
                        max_digits=12,
                        decimal_places=2
                    )
                )
            )
        )
        .order_by('-total_revenue')[:10]
    )

    customer_labels = []
    customer_revenue = []

    for customer in top_customers:

        customer_labels.append(
            customer['customer__name']
        )

        customer_revenue.append(
            float(customer['total_revenue'])
        )

    # ==========================
    # CONTEXT
    # ==========================

    context = {

        # KPI CARDS

        'total_sales': total_sales,
        'total_profit': total_profit,
        'total_expenses': total_expenses,
        'net_profit': net_profit,

        # INVENTORY

        'total_stock': total_stock,
        'total_eggs': total_eggs,
        'low_stock': low_stock,

        # CHARTS

        'daily_labels': daily_labels,
        'daily_values': daily_values,

        'monthly_labels': monthly_labels,
        'monthly_sales_values': monthly_sales_values,
        'monthly_profit_values': monthly_profit_values,

        # CUSTOMERS

        'top_customers': top_customers,
        'customer_labels': customer_labels,
        'customer_revenue': customer_revenue,
    }

    return render(
        request,
        'dashboard/dashboard.html',
        context
    )
#********************************Summary Report*******************************

def summary_report_pdf(request):

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    sales = Sale.objects.all()
    expenses = Expense.objects.all()

    title_text = "Fresg Eggs Business Summary Report"

    if start_date and end_date:

        sales = sales.filter(
            date__range=[
                start_date,
                end_date
            ]
        )

        expenses = expenses.filter(
            date__range=[
                start_date,
                end_date
            ]
        )

        title_text = (
            f"Summary Report "
            f"({start_date} to {end_date})"
        )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        'attachment; '
        'filename="summary_report.pdf"'
    )

    doc = SimpleDocTemplate(response)

    elements = []

    styles = getSampleStyleSheet()

    # =====================================
    # COMPANY HEADER
    # =====================================

    company_name = Paragraph(
        """
        <para align="center">
        <font size="20">
        <b>FRESH EGGS MANAGER</b>
        </font>
        </para>
        """,
        styles['Normal']
    )

    report_title = Paragraph(
        f"""
        <para align="center">
        <font size="14">
        <b>{title_text}</b>
        </font>
        </para>
        """,
        styles['Normal']
    )

    generated_on = Paragraph(
        f"""
        <para align="center">
        Generated On:
        {datetime.now().strftime('%d-%b-%Y %I:%M %p')}
        </para>
        """,
        styles['Normal']
    )

    elements.append(company_name)
    elements.append(Spacer(1, 8))

    elements.append(report_title)
    elements.append(Spacer(1, 8))

    elements.append(generated_on)
    elements.append(Spacer(1, 15))

    if start_date and end_date:

        report_period = Paragraph(
            f"""
            <b>Reporting Period:</b>
            {start_date} to {end_date}
            """,
            styles['BodyText']
        )

        elements.append(report_period)

    else:

        report_period = Paragraph(
            """
            <b>Reporting Period:</b>
            All Records
            """,
            styles['BodyText']
        )

        elements.append(report_period)

    elements.append(Spacer(1, 15))

    total_sales = 0
    total_profit = 0

    for sale in sales:

        total_sales += float(
            sale.revenue
        )

        total_profit += float(
            sale.profit
        )

    total_expenses = sum(
        float(exp.amount)
        for exp in expenses
    )

    total_eggs = sum(
        stock.eggs_remaining
        for stock in Stock.objects.all()
    )

    total_stock = round(
        total_eggs / 30,
        2
    )

    net_profit = (
        total_profit -
        total_expenses
    )

    data = [

        ['Metric', 'Value'],

        [
            'Total Sales',
            f'UGX {total_sales:,.0f}'
        ],

        [
            'Total Expenses',
            f'UGX {total_expenses:,.0f}'
        ],

        [
            'Gross Profit',
            f'UGX {total_profit:,.0f}'
        ],

        [
            'Net Profit',
            f'UGX {net_profit:,.0f}'
        ],

        [
            'Available Stock (Trays)',
            f'{total_stock}'
        ],

        [
            'Available Stock (Eggs)',
            f'{total_eggs}'
        ],
    ]

    table = Table(
        data,
        colWidths=[220, 180]
    )
    table.setStyle(
    TableStyle([

        (
            'BACKGROUND',
            (0, 0),
            (-1, 0),
            colors.HexColor('#003366')
        ),

        (
            'TEXTCOLOR',
            (0, 0),
            (-1, 0),
            colors.white
        ),

        (
            'FONTNAME',
            (0, 0),
            (-1, 0),
            'Helvetica-Bold'
        ),

        (
            'FONTSIZE',
            (0, 0),
            (-1, 0),
            12
        ),

        (
            'GRID',
            (0, 0),
            (-1, -1),
            1,
            colors.black
        ),

        (
            'BACKGROUND',
            (0, 1),
            (-1, -1),
            colors.whitesmoke
        ),

        (
            'ROWBACKGROUNDS',
            (0, 1),
            (-1, -1),
            [
                colors.whitesmoke,
                colors.lightgrey
            ]
        ),

        (
            'ALIGN',
            (0, 0),
            (-1, -1),
            'LEFT'
        ),

    ])
)

    elements.append(table)

    doc.build(elements)

    return response