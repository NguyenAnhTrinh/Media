# Generated by Django 4.2.7 on 2023-12-23 05:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_room_host_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='host_profile',
        ),
    ]