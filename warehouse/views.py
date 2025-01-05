from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from .models import Operation, Photo, CustomUser, DayAlert, Announcement, ManHour
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

from .utils import calculate_man_hours, generate_pdf


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
        'next_operations_table': next_operations,
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


@login_required
def reports(request):

    if request.method == "POST":
        start_date_str = request.POST['start_date']
        start_date = parse_date(start_date_str)
        end_date_str = request.POST['end_date']
        end_date = parse_date(end_date_str)
        customer = request.POST.get('customer', False)
        if not customer or customer == "wszystko":
            customer = None

        operation_type = request.POST.get('operation_type', False)
        if not operation_type or operation_type == "wszystko":
            operation_type = None

        status = request.POST.get('status', False)
        if not status or status == "wszystko":
            status = None

        ramp_number = request.POST.get('ramp_number', False)
        if not ramp_number or ramp_number == "wszystko":
            ramp_number = None

        user = request.POST.get('user', False)
        if user == "mine":
            user = request.user
        else:
            user = None

        operations = Operation.objects.filter(start_time__date__gte=start_date, start_time__date__lte=end_date)

        if customer:
            operations = operations.filter(customer=customer)


        if operation_type:
            operations = operations.filter(operation_type=operation_type)

        if status:
            operations = operations.filter(status=status)

        if ramp_number:
            operations = operations.filter(ramp_number=ramp_number)

        if user:
            operations = operations.filter(user=user)

        for operation in operations:
            print('operation', operation.start_time , operation.customer, operation.operation_type, operation.status)


        print(start_date, end_date, customer, operation_type, status, ramp_number, user)

        operations = operations.order_by('start_time')


        return generate_pdf(operations)

    context = {

    }
    return render(request, 'warehouse/raports.html', context)




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
def man_hours(request):
    man_hours_standard = ManHour.objects.filter(man_hour_type='standard').order_by('-start_date')
    man_hours_exceptional = ManHour.objects.filter(man_hour_type='exceptional').order_by('-start_date')

    context = {'man_hours_standard': man_hours_standard,
               'man_hours_exceptional': man_hours_exceptional,
               }

    return render(request, 'warehouse/man-hours.html', context)


def man_hour_edit(request, man_hour_pk):
    man_hour = ManHour.objects.get(pk=man_hour_pk)


    if request.method == "POST":
        man_hour.start_date = request.POST['start_date']
        man_hour.end_date = request.POST['end_date']
        man_hour.minutes_amount = request.POST['minutes_amount']
        man_hour.man_hour_type = request.POST['man_hour_type']
        man_hour.save()

    context = {}


    return redirect(f'/roboczogodziny')

def man_hour_add(request):

    if request.method == "POST":
        man_hour_start_date = request.POST['start_date']
        man_hour_end_date = request.POST['end_date']
        man_hour_minutes_amount = request.POST['minutes_amount']
        man_hour_man_hour_type = request.POST['man_hour_type']

        man_hour = ManHour(start_date= man_hour_start_date,
                                    end_date=man_hour_end_date, minutes_amount=man_hour_minutes_amount, man_hour_type= man_hour_man_hour_type)
        man_hour.save()

    context = {}


    return redirect(f'/roboczogodziny')

def man_hour_delete(request, man_hour_pk):
    man_hour = ManHour.objects.get(pk=man_hour_pk)
    man_hour.delete()

    return redirect(f'/roboczogodziny')


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

    man_hour_chart = calculate_man_hours(input_date)



    context = {'operations_all': Operation.objects.filter(start_time__date=input_date),
               'operations_ramp1': Operation.objects.filter(start_time__date=input_date, ramp_number='ramp1'),
               'operations_ramp2': Operation.objects.filter(start_time__date=input_date, ramp_number='ramp2'),
               'operations_ramp3': Operation.objects.filter(start_time__date=input_date, ramp_number='ramp3'),
               'alerts': alerts,
               'selected_day': str(input_date),
               'today_date': datetime.now().strftime("%Y-%m-%d"),
               'man_hour_chart': man_hour_chart,
               'generate_report_link': f'raporty/generuj-raport/{input_date}/{input_date}',


               }

    return render(request, 'warehouse/operations.html', context)


@login_required
def operations_list(request, show_only_mine_input='wszystkie', show_only_future_input='wszystkie', operation_status_input='wszystkie'):

    if show_only_mine_input == 'moje':
        show_only_mine= True
    else:
        show_only_mine = False
    if show_only_future_input == 'przyszle':
        show_only_future = True
    else:
        show_only_future = False

    if operation_status_input == 'zaakceptowane':
        operation_status = 'accepted'
        print('taaak')
    elif operation_status_input == 'doakceptacji':
        operation_status = 'pending'
    else:
        operation_status = False

    operations = Operation.objects.all()

    if show_only_mine:
        operations = operations.filter(user=request.user)
    if show_only_future:
        operations = operations.filter(start_time__date__gte=datetime.now().strftime("%Y-%m-%d"))
    if operation_status:
        operations = operations.filter(status=operation_status)


    context = {
               'operations': operations.order_by('-start_time'),
                'show_only_mine': show_only_mine,
                'show_only_future': show_only_future,
                'operation_status': operation_status,
               }

    return render(request, 'warehouse/operations-list.html', context)


def operations_list_filter_select(request):
    if request.method == "POST":

        if request.POST.get('show_only_mine', False):
            show_only_mine = 'moje'
        else:
            show_only_mine = 'wszystko'


        if request.POST.get('show_only_future', False):
            show_only_future = 'przyszle'
        else:
            show_only_future = 'wszystko'

        operation_status = request.POST['operation_status']
        if operation_status:
            if operation_status == 'accepted':
                operation_status = 'zaakceptowane'
            elif operation_status == 'pending':
                operation_status = 'doakceptacji'
        else:
            operation_status = 'wszystko'



        return redirect(f'/lista-operacji/{show_only_mine}/{show_only_future}/{operation_status}')




@login_required
def all_operations(request):



    context = {'operations_future': Operation.objects.filter(start_time__date__gte=datetime.now().strftime("%Y-%m-%d")),
               'operations_all': Operation.objects.filter()
               }

    return render(request, 'warehouse/all-operations.html', context)



def get_monday(year, week):
    # Ustal pierwszy dzień tygodnia zgodnie z ISO-8601
    # Monday (1) = pierwszy dzień tygodnia
    first_day = datetime.strptime(f"{year}-1-1", "%Y-%m-%d")
    first_weekday = first_day.isoweekday()

    # Sprawdź, czy pierwszy tydzień ma >= 4 dni w danym roku
    if first_weekday <= 4:  # Tydzień zaczyna się od tego roku
        delta_days = (week - 1) * 7 - (first_weekday - 1)
    else:  # Tydzień zaczyna się od następnego tygodnia
        delta_days = (week - 1) * 7 + (7 - first_weekday + 1)

    # Oblicz datę poniedziałku
    monday = first_day + timedelta(days=delta_days)
    return monday

@login_required
def operations_week(request, input_year=None, input_week=None):


    if request.method == "POST":
        print('TTRRR')
        week_input = request.POST['week_input']
        year, week = map(int, week_input.split('-W'))  # Parse year and week from input
        print('INPUT WEEK:', week)

        return redirect(f'/operacje/tydzien/{year}/{week}')

    if not input_week or not input_year:
        current_date = datetime.now()
        year, week, _ = current_date.isocalendar()  # Zwraca tuple (rok, tydzień, dzień tygodnia)
        print('week_input',week, year)
    else:
        year, week = int(input_year), int(input_week)


    # Calculate Monday of the selected week
    monday = get_monday(year, week)
    tuesday = monday + timedelta(days=1)
    wednesday = monday + timedelta(days=2)
    thursday = monday + timedelta(days=3)
    friday = monday + timedelta(days=4)

    print('monday',monday, tuesday, wednesday, thursday, friday)

    week_days = {'monday': monday, 'tuesday': tuesday, 'wednesday': wednesday, 'thursday': thursday, 'friday': friday}


    # Filter operations based on the selected week
    context = {
        'operations_all': Operation.objects.filter(start_time__date__gte=monday, end_time__date__lte=friday),
        'operations_monday': Operation.objects.filter(start_time__date=monday),
        'operations_tuesday': Operation.objects.filter(start_time__date=tuesday),
        'operations_wednesday': Operation.objects.filter(start_time__date=wednesday),
        'operations_thursday': Operation.objects.filter(start_time__date=thursday),
        'operations_friday': Operation.objects.filter(start_time__date=friday),
        'selected_week': f"{year}-W{week:02}",
        'today_date': datetime.now().strftime("%Y-%m-%d"),
        'generate_report_link': f'raporty/generuj-raport/{monday.date()}/{friday.date()}',
        'week_days': week_days
    }

    print('friday', friday,  Operation.objects.filter(start_time__date=friday))




    return render(request, 'warehouse/operations-week.html', context)

@login_required
def operation_detail(request, operation_pk):
    operation = Operation.objects.get(pk=operation_pk)

    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        Photo.objects.create(image=image)

    photos = Photo.objects.filter(operation=operation)

    if request.user.role == 'spedytor':
        next_operations = Operation.objects.filter(user=request.user,
                                                   start_time__date__gte=datetime.now().strftime("%Y-%m-%d")).order_by(
            'start_time')[:5]
    else:
        next_operations = Operation.objects.filter(start_time__date__gte=datetime.now().strftime("%Y-%m-%d")).order_by(
            'start_time')[:5]

    year, week, _ = operation.start_time.date().isocalendar()
    context = {
                'operation': operation,
                'photos': photos,
                'next_operations': next_operations,
                'day_url': f'/operacje/dzien/{operation.start_time.date()}',
                'week_url': f'/operacje/tydzien/{year}/{week}',
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
        if request.POST['weight']:
            weight = int(request.POST['weight'])
        else:
            weight = None
        if request.POST['cargo_name']:
            cargo_name = request.POST['cargo_name']
        else:
            cargo_name = None


        user = request.user
        new_operation = Operation.objects.create(user = user, spedition_number=spedition_number, customer=customer, start_time=start_date, end_time=end_date, cut_off=cut_off, operation_type=operation_type, ramp_number=ramp_number, weight=weight, cargo_name=cargo_name)
        new_operation.save()
        print('spedition_number:', spedition_number, 'start_date:', start_date)

        previous_url = request.META.get('HTTP_REFERER', '')
        if 'tydzien' in previous_url:
            print('taak tydzien')
            year, week, _ = new_operation.start_time.isocalendar()  # Zwraca tuple (rok, tydzień, dzień tygodnia)
            print('week_input', week, year)
            return redirect(f'/operacje/tydzien/{year}/{week}')

        else:
            return redirect(f'/operacje/dzien/{new_operation.start_time.date()}')

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
        if request.POST['weight']:
            operation.weight = int(request.POST['weight'])
        else:
            operation.weight = None
        if request.POST['cargo_name']:
            operation.cargo_name = request.POST['cargo_name']
        else:
            operation.cargo_name = None
        operation.operation_type = operation_type
        ramp_number = request.POST['ramp_number']
        operation.ramp_number = ramp_number
        user = request.user

        operation.save()

        return redirect(f'/operacje/{operation.id}')


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


        previous_url = request.META.get('HTTP_REFERER', '')
        print('previous_url', previous_url)

        if 'tydzien' in previous_url:
            print('taak tydzien')
            year, week, _ = operation.start_time.isocalendar()  # Zwraca tuple (rok, tydzień, dzień tygodnia)
            print('week_input', week, year)
            return redirect(f'/operacje/tydzien/{year}/{week}')

        elif 'dzien' in previous_url:
            return redirect(f'/operacje/dzien/{operation.start_time.date()}')
        else:
            return redirect(f'/operacje/{operation.pk}')

    return redirect(f'/operacje/dzien')


def operation_revoke_acceptation(request, operation_pk):
    operation = Operation.objects.get(pk=operation_pk)

    if True:
        operation.status = 'pending'
        operation.save()

        previous_url = request.META.get('HTTP_REFERER', '')
        print('previous_url', previous_url)

        if 'tydzien' in previous_url:
            year, week, _ = operation.start_time.isocalendar()
            return redirect(f'/operacje/tydzien/{year}/{week}')

        elif 'dzien' in previous_url:

            return redirect(f'/operacje/dzien/{operation.start_time.date()}')

        else:

            return redirect(f'/operacje/{operation.pk}')


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

            # Sprawdź format obrazu (domyślnie używamy formatu obrazu)
            image_format = image.format if image.format else 'JPEG'

            # Zapis obrazu do pamięci w odpowiednim formacie
            buffer = BytesIO()
            image.save(buffer, format=image_format)  # Użyj odpowiedniego formatu
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


def generate_report_view(request, input_start_date, input_end_date):
    start_date = parse_date(input_start_date)
    end_date = parse_date(input_end_date)
    operations = Operation.objects.filter(start_time__date__gte=start_date, start_time__date__lte=end_date).order_by('start_time')
    print('operations', operations)
    return generate_pdf(operations)
    previous_url = request.META.get('HTTP_REFERER', '')

    return redirect(previous_url)


