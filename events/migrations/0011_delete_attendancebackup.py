# Generated by Django 4.2.11 on 2024-06-04 23:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_alter_attendance_unique_together'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AttendanceBackup',
        ),
    ]
