# Generated by Django 5.2 on 2025-04-19 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('external_tables', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'managed': False},
        ),
    ]
