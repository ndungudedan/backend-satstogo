# Generated by Django 4.2.11 on 2024-06-04 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_alter_event_access_alter_attendance_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set(),
        ),
    ]
