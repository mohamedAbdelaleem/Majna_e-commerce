# Generated by Django 5.0.1 on 2024-02-01 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brands_applications', '0002_alter_brandapplication_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brandapplication',
            name='authorization_doc',
            field=models.FilePathField(path='authorization_docs/'),
        ),
        migrations.AlterField(
            model_name='brandapplication',
            name='identity_doc',
            field=models.FilePathField(path='identity_docs/'),
        ),
    ]
