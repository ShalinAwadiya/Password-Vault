# Generated by Django 3.2.10 on 2022-03-31 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_media'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='updated_at',
        ),
    ]