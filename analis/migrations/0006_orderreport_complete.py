# Generated by Django 3.0.2 on 2020-02-22 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analis', '0005_orderreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderreport',
            name='complete',
            field=models.BooleanField(default=False),
        ),
    ]
