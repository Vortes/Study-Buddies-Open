# Generated by Django 3.1.7 on 2021-04-19 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0011_auto_20210419_2012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='camera_tag',
            field=models.BooleanField(verbose_name='Group Camera Off'),
        ),
    ]
