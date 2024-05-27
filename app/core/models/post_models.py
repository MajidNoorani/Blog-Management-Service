from django.db import models
from django.utils import timezone
from django.conf import settings
import os
import uuid

def blog_category_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'postCategory', filename)


def post_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'post', filename)


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
    """post category objects"""
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


class Post(AuditModel):
    """Post objects"""
    # note: excerpt and reviewstatus seems to be redundant
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('publish', 'Publish'),
        ('archive', 'Archive'),
    ]
    title = models.CharField(
        max_length=100,
        unique=False,
        verbose_name="Post Title")
    content = models.TextField(verbose_name="Post Content")
    postCategoryId = models.ForeignKey(
        PostCategory,
        null=False,
        blank=False,
        verbose_name="Post Category",
        on_delete=models.RESTRICT
        )
    image = models.ImageField(
        upload_to=post_image_file_path,
        verbose_name="Post Image")
    tags = models.ManyToManyField(
        'Tag',
        verbose_name="Post Tags")
    postStatus = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Post Status")
    postPublishDate = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Post Publish Date")
    postArchivedDate = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Post Archive Date")
    isExternalSource = models.BooleanField(
        verbose_name="Is External Source", default=False)
    externalLink = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="External link")
    commentsEnabled = models.BooleanField(
        null=False,
        blank=False)
    metaDescription = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Meta Description",
        help_text="""
        Stores a brief summary or description of the blog post,
        typically used for SEO purposes and displayed in search engine results.
        """
        )
    seoKeywords = models.ManyToManyField(
        'SEOKeywords',
        verbose_name="SEO Keywords",
        )
    readTime = models.IntegerField(
        verbose_name="Estimated Read Time",
        help_text="""
        Estimates the time required to read the blog post
        """
        )
    relatedPosts = models.ManyToManyField(
        'self',
        blank=True
        )

    def can_change(self, new_status):
        if self.postStatus == 'draft' and new_status in ['draft',
                                                         'publish',
                                                         'archive']:
            return True
        elif self.postStatus == 'publish' and new_status == 'archive':
            return True
        return False

    def change_to(self, new_status):
        if self.can_change(new_status):
            self.postStatus = new_status
            self.save()
        else:
            raise ValueError(
                f"""
                Cannot change status of {self.title} from
                {self.postStatus} to {new_status}
                """
                )

    def __str__(self):
        return self.title


class Tag(AuditModel):
    """Tags for filtering posts."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SEOKeywords(AuditModel):
    """SEO keywrods for the posts."""
    keyword = models.CharField(max_length=255)

    def __str__(self):
        return self.keyword
