# Generated by Django 3.1.4 on 2020-12-16 18:38

from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20201215_2224'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': [django.db.models.functions.text.Lower('osu_name')]},
        ),
        migrations.AddField(
            model_name='match',
            name='score_1',
            field=models.IntegerField(blank=True, null=True, verbose_name='Team 1 Score'),
        ),
        migrations.AddField(
            model_name='match',
            name='score_2',
            field=models.IntegerField(blank=True, null=True, verbose_name='Team 2 Score'),
        ),
        migrations.AlterField(
            model_name='map',
            name='star_rating',
            field=models.DecimalField(decimal_places=3, max_digits=6),
        ),
        migrations.AlterField(
            model_name='score',
            name='accuracy',
            field=models.DecimalField(decimal_places=3, max_digits=6),
        ),
        migrations.AlterField(
            model_name='score',
            name='contrib',
            field=models.DecimalField(decimal_places=3, max_digits=6),
        ),
    ]
