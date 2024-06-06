# Generated by Django 4.2.11 on 2024-06-06 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_rename_withdrawalrequests_withdrawalrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawalrequest',
            name='status',
            field=models.TextField(choices=[('PROCESSING', 'PROCESSING'), ('FAILURE', 'FAILURE'), ('EXPIRED', 'EXPIRED'), ('SUCCESS', 'SUCCESS')], default='PROCESSING', max_length=20),
        ),
    ]