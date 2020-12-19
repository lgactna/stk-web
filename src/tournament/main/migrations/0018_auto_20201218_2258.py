# Generated by Django 3.1.4 on 2020-12-19 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20201218_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='is_player',
            field=models.BooleanField(default=True, help_text="Whether this user is playing or not. If false, disables tournament statistics on this user's page.", verbose_name='Participating in tournament?'),
        ),
        migrations.AlterField(
            model_name='player',
            name='is_staff',
            field=models.BooleanField(default=True, help_text="Whether this user is staffing or not. If false, disables staffing details on this user's page.", verbose_name='Participating in tournament?'),
        ),
    ]
