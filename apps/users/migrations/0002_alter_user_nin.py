# Generated by Django 5.2 on 2025-04-28 13:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='nin',
            field=models.CharField(max_length=11, null=True, validators=[django.core.validators.MinLengthValidator(11)]),
        ),
    ]
