# Generated by Django 5.2 on 2025-04-19 09:01

import apps.common.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.CharField(default=apps.common.models.generate_uuid, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True)),
                ('agent_id', models.IntegerField(null=True, unique=True, validators=[django.core.validators.MinValueValidator(100000)])),
                ('commission', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rating', models.DecimalField(decimal_places=1, default=0.0, max_digits=2)),
                ('status', models.CharField(default='inactive', max_length=20)),
            ],
            options={
                'ordering': ['agent_id'],
            },
        ),
    ]
