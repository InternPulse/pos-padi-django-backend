# Generated by Django 5.2 on 2025-04-16 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.CharField(default='756ab74c-9646-49b9-a7aa-399f5d52fca6', editable=False, max_length=36, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('fee', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('type', models.CharField(max_length=10, null=True)),
                ('rating', models.DecimalField(decimal_places=1, max_digits=2, null=True)),
                ('status', models.CharField(choices=[('successful', 'Successful'), ('failed', 'Failed'), ('pending', 'Pending')], default='pending', max_length=20, null=True)),
            ],
            options={
                'db_table': 'transactions',
                'managed': False,
            },
        ),
    ]
