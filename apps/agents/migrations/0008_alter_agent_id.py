# Generated by Django 5.2 on 2025-04-18 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0007_alter_agent_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='id',
            field=models.CharField(default='1bf3371a-d50f-41a5-98e8-fe7fdda44379', editable=False, max_length=36, primary_key=True, serialize=False),
        ),
    ]
