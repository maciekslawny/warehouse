from django.utils import timezone
from datetime import timedelta

from django.db import models

from django.contrib.auth.models import AbstractUser



class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('spedytor', 'Spedytor'),
        ('magazynier', 'Magazynier'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='spedytor')



class Operation(models.Model):
    OPERATION_CHOICES = [
        ('pallets_loading', 'Załadunek paletowy'),
        ('manual_loading', 'Załadunek ręczny'),
        ('unloading', 'Rozładunek'),
    ]
    RAMP_CHOICES = [
        ('ramp1', 'Rampa 1'),
        ('ramp2', 'Rampa 2'),
        ('ramp3', 'Rampa 3'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Do akceptacji'),
        ('accepted', 'Zaakceptowany'),
    ]
    CUSTOMER_CHOICES = [
        ('erie', 'Erie'),
        ('laktopol', 'Laktopol'),
        ('geti', 'Geti'),
        ('huzar', 'Huzar'),
    ]
    user = models.ForeignKey(
        CustomUser,  # Odwołanie do wbudowanego modelu użytkownika
        on_delete=models.CASCADE,  # Usunięcie użytkownika usuwa jego instancje
        related_name='created_objects',  # Opcjonalnie: alias do odwołania
        verbose_name='Utworzone przez'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    cut_off = models.DateTimeField(blank=True, null=True)
    operation_type = models.CharField(
        max_length=15,
        choices=OPERATION_CHOICES,
        default='loading',
        verbose_name="Typ operacji"
    )

    ramp_number = models.CharField(
        max_length=15,
        choices=RAMP_CHOICES,
        default='ramp1',
        verbose_name="Numer rampy"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    spedition_number = models.CharField(max_length=15)

    customer = models.CharField(
        max_length=20,
        choices=CUSTOMER_CHOICES,
        verbose_name="Klient"
    )

    def get_operation_duration(self):
        # Sprawdź, czy end_time jest naive i przypisz strefę czasową
        end_time = self.end_time
        if end_time.tzinfo is None:
            # Jeżeli end_time jest naive, przypisz strefę czasową
            end_time = timezone.make_aware(end_time)

        # Sprawdź, czy start_time jest naive i przypisz strefę czasową
        start_time = self.start_time
        if start_time.tzinfo is None:
            # Jeżeli start_time jest naive, przypisz strefę czasową
            start_time = timezone.make_aware(start_time)

        # Oblicz różnicę czasu
        duration_seconds = (end_time - start_time).total_seconds()

        print('Czas trwania w sekundach:', duration_seconds)
        return int(duration_seconds)


class Photo(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/')  # Ścieżka, gdzie pliki będą przechowywane
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.id}"