# Generated by Django 5.2 on 2025-04-16 21:13

import apps.common.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.CharField(default='756ab74c-9646-49b9-a7aa-399f5d52fca6', editable=False, max_length=36, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(editable=False, max_length=100, unique=True)),
                ('address', models.CharField(max_length=100)),
                ('registration_number', models.CharField(max_length=9, unique=True)),
                ('logo', models.ImageField(null=True, upload_to='', validators=[apps.common.validators.validate_image_size])),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Companies',
            },
        ),
    ]
