# Generated by Django 2.0.2 on 2018-03-18 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_auto_20180318_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='progress_status',
            field=models.CharField(choices=[('B', 'Behind schedule'), ('O', 'On pace'), ('A', 'Ahead of schedule')], default='B', max_length=1),
        ),
    ]
