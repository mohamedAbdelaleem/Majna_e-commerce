# Generated by Django 5.0.1 on 2024-02-22 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0002_rename_city_id_store_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='name_ar',
            field=models.CharField(default='bla', max_length=50, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='governorate',
            name='name_ar',
            field=models.CharField(default='bla', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]
