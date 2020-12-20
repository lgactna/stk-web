# Generated by Django 3.1.4 on 2020-12-20 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_score_score_difference'),
    ]

    operations = [
        migrations.RenameField(
            model_name='map',
            old_name='bans',
            new_name='ban_count',
        ),
        migrations.RenameField(
            model_name='map',
            old_name='picks',
            new_name='pick_count',
        ),
        migrations.AddField(
            model_name='match',
            name='bans',
            field=models.ManyToManyField(blank=True, related_name='bans', to='main.Map'),
        ),
    ]
