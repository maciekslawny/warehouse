# Generated by Django 5.1.4 on 2024-12-16 16:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0005_rename_created_by_operation_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='photos/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.operation')),
            ],
        ),
    ]