from django.db import models  # noqa
from django.utils import timezone
from django.conf import settings
import os
import uuid


def blog_category_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'blogCategory', filename)


class AuditModel(models.Model):
    createdDate = models.DateTimeField(default=timezone.now)
    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="%(class)s_created_by"
    )
    updatedDate = models.DateTimeField(default=timezone.now)
    updatedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="%(class)s_updated_by"
    )

    class Meta:
        abstract = True


class PostCategory(AuditModel):
    """Recipe objects"""
    title = models.CharField(max_length=100, unique=True)
    parentPostCategoryId = models.ForeignKey('self',
                                             on_delete=models.CASCADE,
                                             null=True,
                                             blank=True,
                                             related_name='children')
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to=blog_category_image_file_path)
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Archived', 'Archived'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Active',
        help_text='Indicates the status of the category'
    )

    def __str__(self):
        return self.title
