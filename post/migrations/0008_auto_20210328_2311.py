# Generated by Django 3.1.7 on 2021-03-28 23:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0007_auto_20210327_0010'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='tags',
            new_name='subject',
        ),
    ]