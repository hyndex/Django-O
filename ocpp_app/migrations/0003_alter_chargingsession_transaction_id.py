# Generated by Django 5.0.3 on 2024-04-03 10:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ocpp_app", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chargingsession",
            name="transaction_id",
            field=models.IntegerField(),
        ),
    ]
