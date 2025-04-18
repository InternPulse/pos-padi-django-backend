# Generated by Django 5.2 on 2025-04-18 09:22

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
                ('id', models.CharField(default='ad1fc95b-6c5f-46ab-8d5a-c9a306e4f0b1', editable=False, max_length=36, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True)),
                ('agent_id', models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(100000)])),
                ('commission', models.DecimalField(decimal_places=5, max_digits=10)),
                ('rating', models.DecimalField(decimal_places=1, default=0.0, max_digits=2)),
                ('status', models.CharField(default='inactive', max_length=20)),
            ],
            options={
                'ordering': ['agent_id'],
            },
        ),
    ]
