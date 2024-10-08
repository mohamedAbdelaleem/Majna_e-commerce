# Generated by Django 4.2.15 on 2024-08-30 16:06

from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_alter_product_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='albumitem',
            name='img_url',
        ),
        migrations.AddField(
            model_name='albumitem',
            name='image',
            field=models.ImageField(default='product.png', upload_to=products.models.product_images_path),
            preserve_default=False,
        ),
    ]
