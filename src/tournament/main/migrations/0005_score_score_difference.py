# Generated by Django 3.1.4 on 2020-12-20 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20201219_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='score_difference',
            field=models.IntegerField(default=0, help_text="The difference between this player's team's total score and the other team's total score. If negative, then it means this player lost that map."),
            preserve_default=False,
        ),
    ]
