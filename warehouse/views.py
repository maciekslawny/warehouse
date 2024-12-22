from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from .models import Operation, Photo, CustomUser, DayAlert, Announcement
from django.utils.dateparse import parse_datetime, parse_date
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Photo
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from .models import Operation
from django.utils import timezone


@login_required
def home(request):

    date_today = datetime.now().strftime("%Y-%m-%d")

    if request.user.role == 'spedytor':
        next_operations = Operation.objects.filter(user=request.user ,start_time__date__gte=date_today).order_by(
        'start_time')
        past_operations_amount = len(Operation.objects.filter(user=request.user, start_time__date__lt=date_today).order_by(
            'start_time'))
        next_operations_amount = len(next_operations)
        pending_operations_amount = len(Operation.objects.filter(user=request.user, status='pending'))
    else:
        next_operations = Operation.objects.filter(start_time__date__gte=date_today).order_by(
            'start_time')
        past_operations_amount = len(Operation.objects.filter(start_time__date__lt=date_today).order_by(
            'start_time'))
        next_operations_amount = len(next_operations)
        pending_operations_amount = len(Operation.objects.filter(status='pending'))



    context = {
        'next_operations': next_operations[:5],
        'past_operations_amount': past_operations_amount,
        'next_operations_amount': next_operations_amount,
        'pending_operations_amount': pending_operations_amount,
        'announcements': Announcement.objects.all().order_by('-created_datetime'),

    }
    return render(request, 'warehouse/index.html', context)

@login_required
def statistics(request):





    context = {

    }
    return render(request, 'warehouse/statistics.html', context)




def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Nieprawidłowy login lub hasło.")
    return render(request, 'warehouse/login-page.html')


def logout_view(request):
    logout(request)  # Wylogowanie użytkownika
    return redirect('/zaloguj')  # Przekierowanie na stronę logowania lub inną stronę

@login_required
def accounts(request, input_date=datetime.now().strftime("%Y-%m-%d")):
    users = CustomUser.objects.all()



    context = {'users': users,
               }

    return render(request, 'warehouse/accounts.html', context)


@login_required
def announcements(request):
    announcements = Announcement.objects.all().order_by('-created_datetime')

    context = {'announcements': announcements,
               }

    return render(request, 'warehouse/announcements.html', context)


def announcement_edit(request, announcement_pk):
    announcement = Announcement.objects.get(pk=announcement_pk)


    if request.method == "POST":
        announcement_title = request.POST['announcement_title']
        announcement.title = announcement_title
        announcement_message = request.POST['announcement_message']
        announcement.message = announcement_message
        announcement.save()

    context = {}


    return redirect(f'/komunikaty')


def announcement_delete(request, announcement_pk):
    announcement = Announcement.objects.get(pk=announcement_pk)
    announcement.delete()

    return redirect(f'/komunikaty')


def announcement_add(request):



    if request.method == "POST":
        announcement_title = request.POST['announcement_title']
        announcement_message = request.POST['announcement_message']
        announcement_added_by = request.user

        announcement = Announcement(title=announcement_title,
                                    message=announcement_message, added_by=announcement_added_by)
        announcement.save()

    context = {}


    return redirect(f'/komunikaty')


@login_required
def day_alerts(request):
    day_alerts = DayAlert.objects.all().order_by('-date')

    context = {'day_alerts': day_alerts,
               }

    return render(request, 'warehouse/day-alerts.html', context)


def day_alert_edit(request, day_alert_pk):
    day_alert = DayAlert.objects.get(pk=day_alert_pk)


    if request.method == "POST":
        day_alert_message = request.POST['day_alert_message']
        day_alert.message = day_alert_message
        day_alert_date = request.POST['day_alert_date']
        day_alert.date = parse_date(day_alert_date)
        day_alert.save()

    context = {}


    return redirect(f'/alerty')


def day_alert_delete(request, day_alert_pk):
    day_alert = DayAlert.objects.get(pk=day_alert_pk)
    day_alert.delete()

    return redirect(f'/alerty')


def day_alert_add(request):



    if request.method == "POST":
        day_alert_message = request.POST['day_alert_message']
        day_alert_date = parse_date(request.POST['day_alert_date'])
        day_alert_added_by = request.user

        day_alert = DayAlert(date= day_alert_date,
                                    message=day_alert_message, added_by=day_alert_added_by)
        day_alert.save()

    context = {}


    return redirect(f'/alerty')










@login_required
def operations(request, input_date=None):
    if not input_date:
        input_date = timezone.now().strftime("%Y-%m-%d")
    input_date = datetime.strptime(input_date, '%Y-%m-%d').date()
    alerts = DayAlert.objects.filter(date=input_date)
    print('alerts',alerts)



    context = {'operations_all': Operation.objects.filter(start_time__date=input_date),
               'operations_ramp1': Operation.objects.filter(start_time__date=input_date, ramp_number='ramp1'),
               'operations_ramp2': Operation.objects.filter(start_time__date=input_date, ramp_number='ramp2'),
               'operations_ramp3': Operation.objects.filter(start_time__date=input_date, ramp_number='ramp3'),
               'alerts': alerts,
               'selected_day': str(input_date),


               }

    return render(request, 'warehouse/operations.html', context)


@login_required
def my_operations(request):



    context = {'operations_future': Operation.objects.filter(start_time__date__gte=datetime.now().strftime("%Y-%m-%d"), user=request.user),
               'operations_all': Operation.objects.filter(user=request.user)
               }

    return render(request, 'warehouse/my-operations.html', context)


@login_required
def all_operations(request):



    context = {'operations_future': Operation.objects.filter(start_time__date__gte=datetime.now().strftime("%Y-%m-%d")),
               'operations_all': Operation.objects.filter()
               }

    return render(request, 'warehouse/all-operations.html', context)

@login_required
def operations_week(request, input_date=datetime.now().strftime("%Y-%m-%d")):
    input_date = datetime.strptime(input_date, '%Y-%m-%d').date()
    print(input_date)

    monday = datetime.strptime('2024-12-16', "%Y-%m-%d")
    tuesday = datetime.strptime('2024-12-17', "%Y-%m-%d")
    wednesday = datetime.strptime('2024-12-18', "%Y-%m-%d")
    thursday = datetime.strptime('2024-12-19', "%Y-%m-%d")
    friday = datetime.strptime('2024-12-20', "%Y-%m-%d")

    context = {'operations_all': Operation.objects.filter(start_time__date__gte=monday, end_time__lte=friday),
               'operations_monday': Operation.objects.filter(start_time__date=monday),
               'operations_tuesday': Operation.objects.filter(start_time__date=tuesday),
               'operations_wednesday': Operation.objects.filter(start_time__date=wednesday),
               'operations_thursday': Operation.objects.filter(start_time__date=thursday),
               'operations_friday': Operation.objects.filter(start_time__date=friday),
               'selected_day': str(input_date),

               }

    return render(request, 'warehouse/operations-week.html', context)

@login_required
def operation_detail(request, operation_pk):

    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        Photo.objects.create(image=image)

    photos = Photo.objects.filter(operation=Operation.objects.get(pk=operation_pk))

    if request.user.role == 'spedytor':
        next_operations = Operation.objects.filter(user=request.user,
                                                   start_time__date__gte=datetime.now().strftime("%Y-%m-%d")).order_by(
            'start_time')[:5]
    else:
        next_operations = Operation.objects.filter(start_time__date__gte=datetime.now().strftime("%Y-%m-%d")).order_by(
            'start_time')[:5]


    context = {
                'operation': Operation.objects.get(pk=operation_pk),
                'photos': photos,
                'next_operations': next_operations,
               }

    return render(request, 'warehouse/operation-card.html', context)

@login_required
def operation_add(request):

    context = {'today_date': datetime.now().strftime("%Y-%m-%d")}
    if request.method == "POST":
        spedition_number = request.POST['spedition_number']
        customer = request.POST['customer']
        start_date_str = request.POST['start_date']
        print('tak wyglada', str(start_date_str))
        start_date = parse_datetime(start_date_str)
        end_date_str = request.POST['end_date']
        end_date = parse_datetime(end_date_str)
        cut_off_str = request.POST['cut_off']
        if cut_off_str:
            cut_off = parse_datetime(cut_off_str)
        else:
            cut_off = None
        operation_type = request.POST['operation_type']
        ramp_number = request.POST['ramp_number']
        user = request.user
        new_operation = Operation.objects.create(user = user, spedition_number=spedition_number, customer=customer, start_time=start_date, end_time=end_date, cut_off=cut_off, operation_type=operation_type, ramp_number=ramp_number)
        new_operation.save()
        print('spedition_number:', spedition_number, 'start_date:', start_date)

    return render(request, 'warehouse/operation-add.html', context)

@login_required
def operation_edit(request, operation_pk):

    operation = Operation.objects.get(pk=operation_pk)


    if request.method == "POST":
        spedition_number = request.POST['spedition_number']
        operation.spedition_number = spedition_number
        customer = request.POST['customer']
        operation.customer = customer
        start_date_str = request.POST['start_date']
        print('tak wyglada', str(start_date_str))
        start_date = parse_datetime(start_date_str)
        operation.start_time = start_date

        end_date_str = request.POST['end_date']
        end_date = parse_datetime(end_date_str)
        operation.end_time = end_date
        cut_off_str = request.POST['cut_off']
        if cut_off_str:
            cut_off = parse_datetime(cut_off_str)
        else:
            cut_off = None
        operation.cut_off = cut_off
        operation_type = request.POST['operation_type']
        operation.operation_type = operation_type
        ramp_number = request.POST['ramp_number']
        operation.ramp_number = ramp_number
        user = request.user

        operation.save()

    context = {'today_date': datetime.now().strftime("%Y-%m-%d"),
               'operation': operation}

    return render(request, 'warehouse/operation-edit.html', context)



def operation_select_date(request):

    if request.method == "POST":
        selected_date = request.POST['selected_date']

        return redirect(f'/operacje/dzien/{selected_date}')

    return redirect(f'/operacje/dzien')


def operation_acceptation(request, operation_pk):

    operation = Operation.objects.get(pk=operation_pk)

    from django.utils import timezone

    if request.method == "POST":
        acceptation_datetime = request.POST['acceptation_datetime']
        ramp_number = request.POST['ramp_number']
        if acceptation_datetime:
            acceptation_datetime = parse_datetime(acceptation_datetime)


            new_time = acceptation_datetime + timedelta(seconds=operation.get_operation_duration())
            operation.start_time = acceptation_datetime

            if new_time.tzinfo is None:
                new_time = timezone.make_aware(new_time)
            print('nowy czas',new_time)
            operation.end_time = new_time
            operation.save()

        operation.ramp_number = ramp_number
        operation.status = 'accepted'
        operation.save()

        return redirect(f'/operacje/dzien/{operation.start_time.date()}')

    return redirect(f'/operacje/dzien')


def operation_revoke_acceptation(request, operation_pk):
    operation = Operation.objects.get(pk=operation_pk)

    if True:
        operation.status = 'pending'
        operation.save()

        return redirect(f'/operacje/dzien/{operation.start_time.date()}')

    return redirect(f'/operacje/dzien')



def upload_photos(request, operation_pk):
    # Pobierz obiekt operacji
    operation = Operation.objects.get(pk=operation_pk)

    if request.method == 'POST':
        # Pobierz przesłane pliki
        images = request.FILES.getlist('image')

        if not images:
            print("Nie przesłano żadnych zdjęć.")
            return redirect(f'/operacje/{operation_pk}')

        for uploaded_image in images:
            # Otwórz obraz za pomocą Pillow
            image = Image.open(uploaded_image)

            # Skalowanie do maksymalnego rozmiaru
            max_size = (800, 800)
            image.thumbnail(max_size)

            # Zapis obrazu do pamięci
            buffer = BytesIO()
            image.save(buffer, format='JPEG')
            buffer.seek(0)

            # Zapisz obraz w modelu
            photo = Photo(operation=operation)
            photo.image.save(uploaded_image.name, ContentFile(buffer.read()), save=False)
            photo.save()

        return redirect(f'/operacje/{operation_pk}')

    return redirect(f'/operacje/{operation_pk}')

def delete_photo(request, photo_pk):

    if request.method == 'POST':
        photo = Photo.objects.get(pk=photo_pk)
        operation_pk = photo.operation.pk
        photo.delete()

    return redirect(f'/operacje/{operation_pk}')


def generate_pdf(request):
    # Ustawienie odpowiedzi jako PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="zestawienie_operacji.pdf"'

    # Tworzenie dokumentu PDF (pionowe A4)
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=1 * cm, bottomMargin=1 * cm, leftMargin=1 * cm,
                            rightMargin=1 * cm)
    elements = []

    # Style
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontSize = 20
    title_style.alignment = 1  # Wyśrodkowanie

    subtitle_style = styles['Heading2']
    subtitle_style.fontSize = 12
    subtitle_style.alignment = 1  # Wyśrodkowanie

    # Dodanie dużego nagłówka
    title = Paragraph("Zestawienie operacji zaladunkowych i wyladunkowych", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Pobieranie danych z modelu Operation
    operations = Operation.objects.order_by('start_time')  # Sortowanie po czasie rozpoczęcia

    # Grupowanie operacji według daty
    grouped_operations = {}
    for operation in operations:
        operation_date = operation.start_time.date()
        if operation_date not in grouped_operations:
            grouped_operations[operation_date] = []
        grouped_operations[operation_date].append(operation)

    # Generowanie tabelek dla każdej daty
    for date, operations in grouped_operations.items():
        # Nagłówek daty
        subtitle = Paragraph(f"Data: {date}", subtitle_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 10))

        # Przygotowanie danych do tabeli
        data = [
            ['Start', 'Koniec', 'Typ', 'Klient', 'Rampa', 'Status']
        ]
        for operation in operations:
            data.append([
                operation.start_time.strftime('%H:%M'),
                operation.end_time.strftime('%H:%M'),
                dict(Operation.OPERATION_CHOICES).get(operation.operation_type, 'N/A'),
                dict(Operation.CUSTOMER_CHOICES).get(operation.customer, 'N/A'),
                dict(Operation.RAMP_CHOICES).get(operation.ramp_number, 'N/A'),
                dict(Operation.STATUS_CHOICES).get(operation.status, 'N/A'),
            ])

        # Tworzenie tabeli
        col_widths = [2.5 * cm, 2.5 * cm, 4 * cm, 4 * cm, 2.5 * cm, 3 * cm]  # Szerokości kolumn
        table = Table(data, colWidths=col_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Tło nagłówka tabeli
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Tekst w nagłówku
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Wyśrodkowanie tekstu
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Pogrubiony nagłówek
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Zwykły tekst
            ('FONTSIZE', (0, 0), (-1, -1), 8),  # Mniejszy rozmiar czcionki
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Odstępy w nagłówku
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),  # Wyrównanie pionowe
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Siatka tabeli
        ])
        table.setStyle(style)

        # Dodanie tabeli do dokumentu
        elements.append(table)
        elements.append(Spacer(1, 15))  # Odstęp między tabelkami

    # Budowanie dokumentu
    doc.build(elements)

    return response


