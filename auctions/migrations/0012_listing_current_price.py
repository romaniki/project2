# Generated by Django 3.1.2 on 2020-12-25 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_auto_20201025_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='current_price',
            field=models.IntegerField(default=0),
        ),
    ]
