# Generated by Django 4.2.7 on 2023-12-27 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_delete_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='password',
        ),
    ]