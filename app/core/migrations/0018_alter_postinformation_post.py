# Generated by Django 5.0.6 on 2024-06-19 07:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_alter_postinformation_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postinformation',
            name='post',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.post'),
        ),
    ]
