# Generated by Django 3.1.7 on 2021-03-26 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='max_buddies',
            field=models.IntegerField(default=5),
        ),
    ]