# Generated by Django 3.1.4 on 2020-12-16 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20201216_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='star_rating_alt',
            field=models.DecimalField(blank=True, decimal_places=3, help_text="The map's star rating after applying mods.", max_digits=6, null=True, verbose_name='Post-mod SR'),
        ),
        migrations.AlterField(
            model_name='map',
            name='ar_alt',
            field=models.DecimalField(blank=True, decimal_places=3, help_text="The map's approach rate after applying mods.", max_digits=5, null=True, verbose_name='Post-mod AR'),
        ),
        migrations.AlterField(
            model_name='map',
            name='cs_alt',
            field=models.DecimalField(blank=True, decimal_places=3, help_text="The map's circle size after applying mods.", max_digits=5, null=True, verbose_name='Post-mod CS'),
        ),
        migrations.AlterField(
            model_name='map',
            name='hp_alt',
            field=models.DecimalField(blank=True, decimal_places=3, help_text="The map's HP drain after applying mods.", max_digits=5, null=True, verbose_name='Post-mod HP'),
        ),
        migrations.AlterField(
            model_name='map',
            name='od_alt',
            field=models.DecimalField(blank=True, decimal_places=3, help_text="The map's overall difficulty after applying mods.", max_digits=5, null=True, verbose_name='Post-mod OD'),
        ),
    ]
