# Generated by Django 5.2 on 2025-04-14 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('external_tables', '0003_alter_agent_id_alter_companyloyaltypoints_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='id',
            field=models.CharField(default='fded4313-4bef-4c8a-8979-105b0919abea', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='companyloyaltypoints',
            name='id',
            field=models.CharField(default='fded4313-4bef-4c8a-8979-105b0919abea', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='customer',
            name='id',
            field=models.CharField(default='fded4313-4bef-4c8a-8979-105b0919abea', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='id',
            field=models.CharField(default='fded4313-4bef-4c8a-8979-105b0919abea', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
    ]
