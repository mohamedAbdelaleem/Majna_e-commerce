# Generated by Django 4.2.15 on 2024-08-24 20:24

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0007_alter_city_governorate_alter_store_city_and_more'),
        ('orders', '0003_alter_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='store',
        ),
        migrations.CreateModel(
            name='OrderItemStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reserved_quantity', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.orderitem')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='addresses.store')),
            ],
        ),
        migrations.AddField(
            model_name='orderitem',
            name='stores',
            field=models.ManyToManyField(through='orders.OrderItemStore', to='addresses.store'),
        ),
    ]
