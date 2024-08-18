# Generated by Django 4.2.15 on 2024-08-13 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0007_alter_city_governorate_alter_store_city_and_more'),
        ('products', '0006_favoriteitem_favoriteitem_unique_favorite_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='albumitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_items', to='products.product'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='addresses.store'),
        ),
        migrations.AlterField(
            model_name='product',
            name='stores',
            field=models.ManyToManyField(through='products.Inventory', to='addresses.store'),
        ),
    ]