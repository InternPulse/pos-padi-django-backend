# Generated by Django 5.2 on 2025-04-18 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0010_alter_agent_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='id',
            field=models.CharField(default='c8d700cb-892e-4ab0-a05f-ba279ea9ffc5', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
    ]
