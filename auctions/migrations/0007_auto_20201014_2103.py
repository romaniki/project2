# Generated by Django 3.1.2 on 2020-10-14 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20201011_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='item',
            field=models.ManyToManyField(to='auctions.Listing'),
        ),
        migrations.AddField(
            model_name='listing',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
