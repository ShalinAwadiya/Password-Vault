# Generated by Django 3.2.10 on 2022-03-30 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_usermpin'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermpin',
            name='encrypted_ciphertext',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='usermpin',
            name='encrypted_remainder',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]