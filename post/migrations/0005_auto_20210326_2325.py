# Generated by Django 3.1.7 on 2021-03-26 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0004_auto_20210326_2321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='max_buddies',
            field=models.IntegerField(choices=[(5, 'Small 1-5'), (10, 'Medium 1-10'), (20, 'Large 1-20')]),
        ),
    ]
