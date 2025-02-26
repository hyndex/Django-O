# Generated by Django 5.0.3 on 2024-04-03 11:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_alter_sessionbilling_amount_consumed_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paymentinfo",
            name="captured",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="paymentinfo",
            name="currency",
            field=models.CharField(default="INR", max_length=3),
        ),
        migrations.AlterField(
            model_name="paymentinfo",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="paymentinfo",
            name="method",
            field=models.CharField(default="WALLET", max_length=255),
        ),
        migrations.AlterField(
            model_name="paymentinfo",
            name="payment_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="paymentinfo",
            name="phone",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name="paymentinfo",
            name="status",
            field=models.CharField(default="PAID", max_length=50),
        ),
    ]
