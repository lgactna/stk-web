# Generated by Django 3.1.4 on 2020-12-16 19:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20201216_1108'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='score',
            name='team',
        ),
    ]