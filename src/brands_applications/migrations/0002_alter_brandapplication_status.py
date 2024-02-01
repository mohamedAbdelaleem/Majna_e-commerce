# Generated by Django 4.2.7 on 2024-01-28 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brands_applications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brandapplication',
            name='status',
            field=models.CharField(choices=[('inprogress', 'In Progress'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='inprogress', max_length=20),
        ),
    ]