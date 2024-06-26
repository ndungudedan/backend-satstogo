# Generated by Django 4.2.11 on 2024-05-27 22:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_satsuserprofile'),
        ('events', '0004_remove_event_deadline_attendance_employee_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='event',
        ),
        migrations.AddField(
            model_name='attendance',
            name='eventSession',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='events.eventsession'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.satsuser'),
        ),
    ]
