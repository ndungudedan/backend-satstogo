# Generated by Django 4.2.11 on 2024-06-18 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_alter_eventsession_deadline_string'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='org_username',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='eventsession',
            name='deadline_string',
            field=models.TextField(blank=True, null=True),
        ),
    ]