# Generated by Django 2.0.2 on 2018-03-17 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('enrollment_email', models.EmailField(max_length=254)),
                ('enrollment_date', models.DateField()),
                ('course_end_date', models.DateField()),
                ('edx_id', models.IntegerField()),
                ('edx_email', models.EmailField(max_length=254)),
                ('edx_username', models.CharField(max_length=50)),
                ('lesson2_score', models.DecimalField(decimal_places=2, max_digits=3)),
                ('lesson3_score', models.DecimalField(decimal_places=2, max_digits=3)),
                ('lesson4_score', models.DecimalField(decimal_places=2, max_digits=3)),
                ('lesson5_score', models.DecimalField(decimal_places=2, max_digits=3)),
                ('lesson6_score', models.DecimalField(decimal_places=2, max_digits=3)),
                ('lesson7_score', models.DecimalField(decimal_places=2, max_digits=3)),
                ('lesson8_score', models.DecimalField(decimal_places=2, max_digits=3)),
                ('lesson9_score', models.DecimalField(decimal_places=2, max_digits=3)),
                ('lesson10_score', models.DecimalField(decimal_places=2, max_digits=3)),
                ('welcome_email_sent', models.BooleanField(default=False)),
                ('week1_email_sent', models.BooleanField(default=False)),
                ('month1_email_sent', models.BooleanField(default=False)),
                ('month2_email_sent', models.BooleanField(default=False)),
                ('month3_email_sent', models.BooleanField(default=False)),
            ],
        ),
    ]
