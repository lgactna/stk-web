# Generated by Django 3.1.4 on 2020-12-19 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20201218_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='is_staff',
            field=models.BooleanField(default=False, help_text="Whether this user is staffing or not. If false, disables staffing details on this user's page.", verbose_name='Participating in tournament?'),
        ),
    ]
