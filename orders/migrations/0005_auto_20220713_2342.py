# Generated by Django 3.1 on 2022-07-13 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_payment_amount_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(default='New', max_length=10),
        ),
    ]
