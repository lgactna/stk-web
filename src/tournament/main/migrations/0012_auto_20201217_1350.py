# Generated by Django 3.1.4 on 2020-12-17 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20201217_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='utc_offset',
            field=models.IntegerField(default=0, help_text="This player's UTC offset. If a player is UTC-8, put -8 here. Note that this doesn't update automatically for DST switches! If this field is used for easy time conversions, make sure the players keep this accurate!", verbose_name='UTC offset'),
        ),
    ]
