from .models import ManHour, Operation


def calculate_man_hours(input_day):
    print(input_day)

    # Pobierz odpowiedni wpis ManHour
    man_hour = ManHour.objects.filter(
        start_date__lte=input_day,
        end_date__gte=input_day,
        man_hour_type='exceptional'
    ).first()

    if not man_hour:
        man_hour = ManHour.objects.filter(
            start_date__lte=input_day,
            end_date__gte=input_day
        ).first()

    # Oblicz ilość minut z ManHour
    man_hour_amount = man_hour.minutes_amount if man_hour else 0

    # Pobierz wszystkie operacje dla danego dnia
    operations_all = Operation.objects.filter(start_time__date=input_day)

    # Przygotuj słownik wynikowy
    result_dict = {'types': {}, 'all_used': 0, 'remaining': 0, 'total': man_hour_amount}

    # Grupuj czas operacji według typu
    for operation in operations_all:
        operation_duration_minutes = operation.get_operation_duration() / 60  # Przelicz sekundy na minuty
        if operation.get_operation_type_display() in result_dict['types']:
            result_dict['types'][operation.get_operation_type_display()] += operation_duration_minutes
        else:
            result_dict['types'][operation.get_operation_type_display()] = operation_duration_minutes

    # Oblicz łączny czas wykorzystany
    all_used = sum(result_dict['types'].values())

    # Uzupełnij pozostałe wartości w słowniku wynikowym
    result_dict['all_used'] = all_used
    result_dict['remaining'] = man_hour_amount - all_used

    return result_dict



from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# Rejestracja czcionki obsługującej polskie znaki
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))


def generate_pdf(queryset):
    """
    Generowanie PDF na podstawie przekazanego querysetu modelu Operation z obsługą polskich znaków.
    """
    # Ustawienie odpowiedzi jako PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="zestawienie_operacji.pdf"'

    # Tworzenie dokumentu PDF (pionowe A4)
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
        leftMargin=0.5 * cm,
        rightMargin=0.5 * cm,
    )
    elements = []

    # Style
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'DejaVuSans'  # Ustawienie czcionki dla tekstów
    title_style = styles['Title']
    title_style.fontName = 'DejaVuSans'
    title_style.fontSize = 18  # Zmniejszony tytuł
    title_style.alignment = 1  # Wyśrodkowanie

    subtitle_style = styles['Heading2']
    subtitle_style.fontName = 'DejaVuSans'
    subtitle_style.fontSize = 10  # Zmniejszona czcionka nagłówka daty
    subtitle_style.alignment = 1  # Wyśrodkowanie

    # Dodanie daty wygenerowania raportu
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_paragraph = Paragraph(f"Data wygenerowania raportu: {current_date}", styles['Normal'])
    elements.append(date_paragraph)
    elements.append(Spacer(1, 10))

    # Dodanie dużego nagłówka
    title = Paragraph("Zestawienie operacji załadunkowych i wyładunkowych", title_style)
    elements.append(title)
    elements.append(Spacer(1, 15))

    # Grupowanie operacji według daty
    grouped_operations = {}
    for operation in queryset:
        operation_date = operation.start_time.date()
        if operation_date not in grouped_operations:
            grouped_operations[operation_date] = []
        grouped_operations[operation_date].append(operation)

    # Generowanie tabelek dla każdej daty
    for date, operations in grouped_operations.items():
        # Nagłówek daty
        subtitle = Paragraph(f"Data: {date}", subtitle_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 8))

        # Przygotowanie danych do tabeli
        headers = ['Start', 'Koniec', 'Typ', 'Klient', 'Rampa', 'Status', 'Spedycja', 'Waga (kg)', 'Ładunek']
        data = [headers]
        rows = []

        for operation in operations:
            rows.append([
                operation.start_time.strftime('%H:%M'),
                operation.end_time.strftime('%H:%M'),
                dict(operation.OPERATION_CHOICES).get(operation.operation_type, 'N/A'),
                dict(operation.CUSTOMER_CHOICES).get(operation.customer, 'N/A'),
                dict(operation.RAMP_CHOICES).get(operation.ramp_number, 'N/A'),
                dict(operation.STATUS_CHOICES).get(operation.status, 'N/A'),
                operation.spedition_number,
                operation.weight or 'N/A',
                operation.cargo_name or 'N/A',
            ])
        data.extend(rows)

        # Obliczanie dynamicznych szerokości kolumn
        font_name = 'DejaVuSans'
        font_size = 7  # Czcionka używana w tabeli
        max_widths = [0] * len(headers)

        # Sprawdzenie maksymalnej szerokości tekstu w każdej kolumnie
        from reportlab.pdfbase.pdfmetrics import stringWidth
        for row in data:
            for col_idx, cell in enumerate(row):
                cell_width = stringWidth(str(cell), font_name, font_size)
                if cell_width > max_widths[col_idx]:
                    max_widths[col_idx] = cell_width

        # Normalizacja szerokości, aby zmieścić tabelę na stronie A4
        total_width = sum(max_widths)
        available_width = A4[0] - 1 * cm  # Szerokość strony A4 minus marginesy
        col_widths = [(w / total_width) * available_width for w in max_widths]

        # Tworzenie tabeli
        table = Table(data, colWidths=col_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Tło nagłówka tabeli
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Tekst w nagłówku
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Wyśrodkowanie tekstu
            ('FONTNAME', (0, 0), (-1, -1), font_name),  # Ustawienie czcionki
            ('FONTSIZE', (0, 0), (-1, -1), font_size),  # Rozmiar czcionki
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),  # Odstępy w nagłówku
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),  # Wyrównanie pionowe
            ('GRID', (0, 0), (-1, -1), 0.3, colors.black),  # Siatka tabeli
        ])
        table.setStyle(style)

        # Dodanie tabeli do dokumentu
        elements.append(table)
        elements.append(Spacer(1, 10))  # Odstęp między tabelkami

    # Budowanie dokumentu
    doc.build(elements)

    return response
