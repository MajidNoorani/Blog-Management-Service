# Generated by Django 5.0.6 on 2024-06-08 14:35

import djrichtextfield.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_post_authorname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=djrichtextfield.models.RichTextField(verbose_name='Post Content'),
        ),
    ]
