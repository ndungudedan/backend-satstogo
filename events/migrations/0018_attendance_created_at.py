# Generated by Django 4.2.11 on 2024-06-19 22:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_remove_attendance_user_magic_attendance_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]