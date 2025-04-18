# Generated by Django 5.2 on 2025-04-17 13:08

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.CharField(default='9e9fe67f-4f8f-4cd6-b17d-88a264572aa6', editable=False, max_length=36, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True)),
                ('agent_id', models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(100000)])),
                ('commission', models.DecimalField(decimal_places=5, max_digits=10)),
                ('rating', models.DecimalField(decimal_places=1, default=0.0, max_digits=2)),
                ('status', models.CharField(default='inactive', max_length=20)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['agent_id'],
            },
        ),
    ]
