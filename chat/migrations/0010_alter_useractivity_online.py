# Generated by Django 4.1.3 on 2022-11-23 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_message_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useractivity',
            name='online',
            field=models.DateTimeField(),
        ),
    ]
