# Generated by Django 5.1.4 on 2024-12-15 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='customer',
            field=models.CharField(choices=[('erie', 'Erie'), ('laktopol', 'Laktopol'), ('geti', 'Geti'), ('huzar', 'Huzar')], default='', max_length=20, verbose_name='Klient'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='operation',
            name='operation_type',
            field=models.CharField(choices=[('pallets_loading', 'Załadunek paletowy'), ('manual_loading', 'Załadunek ręczny'), ('unloading', 'Rozładunek')], default='loading', max_length=15, verbose_name='Typ operacji'),
        ),
    ]