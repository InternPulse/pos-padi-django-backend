# Generated by Django 5.2 on 2025-04-17 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.CharField(default='113fe1bb-be04-4ddd-8c3c-ea206aad083c', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
    ]
