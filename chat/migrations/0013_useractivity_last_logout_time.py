# Generated by Django 4.1.3 on 2022-11-23 11:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0012_useractivity_last_online_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivity',
            name='last_logout_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
