# Generated by Django 4.2.15 on 2024-08-24 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_status_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(choices=[(1, 'Placed'), (2, 'Shipped'), (3, 'Delivered')], default=1),
        ),
    ]
