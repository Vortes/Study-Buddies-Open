# Generated by Django 3.1.7 on 2021-04-18 20:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0008_auto_20210328_2311'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('tag_name',)},
        ),
    ]
