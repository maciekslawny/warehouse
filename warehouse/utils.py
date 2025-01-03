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
