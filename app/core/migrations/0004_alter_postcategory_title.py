# Generated by Django 5.0.6 on 2024-05-22 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_updateddby_postcategory_updatedby'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcategory',
            name='title',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
