# Generated by Django 5.2 on 2025-04-18 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.CharField(default='122d918f-2971-47d7-bcf8-e43d7f0e27ff', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
    ]
