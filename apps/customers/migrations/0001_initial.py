# Generated by Django 5.2 on 2025-04-18 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.CharField(default='ad1fc95b-6c5f-46ab-8d5a-c9a306e4f0b1', editable=False, max_length=36, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True)),
                ('customer_id', models.CharField(max_length=6, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='customer_photos/')),
                ('tag', models.CharField(choices=[('vip', 'VIP'), ('frequent', 'Frequent'), ('regular', 'Regular'), ('inactive', 'Inactive')], default='regular', help_text='Customer classification for segmentation', max_length=10)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CustomerLoyaltyPoints',
            fields=[
                ('id', models.CharField(default='ad1fc95b-6c5f-46ab-8d5a-c9a306e4f0b1', editable=False, max_length=36, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True)),
                ('loyalty_points', models.IntegerField(default=0)),
            ],
        ),
    ]
