# Generated by Django 3.1.4 on 2020-12-19 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20201218_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='country_rank',
            field=models.IntegerField(blank=True, help_text="This user's country rank. Updated ~daily-hourly via celery, shouldn't need to be manual.", null=True, verbose_name='osu! rank'),
        ),
        migrations.AddField(
            model_name='player',
            name='tournament_rank',
            field=models.IntegerField(blank=True, help_text="This user's tournament ranking, by pp. Updated ~daily-hourly via celery, shouldn't need to be manual.", null=True, verbose_name='Tournament rank'),
        ),
    ]
