# Generated by Django 5.0.6 on 2024-06-17 16:42

import core.models.post_models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_rename_postdetail_postanalytics_alter_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcategory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.post_models.blog_category_image_file_path),
        ),
        migrations.AlterUniqueTogether(
            name='postrate',
            unique_together={('user', 'post')},
        ),
    ]
