# Generated by Django 5.2 on 2025-04-17 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.CharField(default='1747e8a8-f8ca-4d5d-b150-1912e482f757', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
    ]
