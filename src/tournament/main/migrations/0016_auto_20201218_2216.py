# Generated by Django 3.1.4 on 2020-12-19 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20201218_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='discord_name',
            field=models.CharField(blank=True, help_text="The player's Discord tag (with discriminator).", max_length=100, null=True),
        ),
    ]