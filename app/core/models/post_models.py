from django.db import models
from django.utils import timezone
import os
import uuid
# from djrichtextfield.models import RichTextField
from django_ckeditor_5.fields import CKEditor5Field
# from ckeditor.fields import RichTextField
# from django_quill.fields import QuillField
from ._base_models import AuditModel
from django.conf import settings
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError


def blog_category_image_file_path(instance, filename):
    """Generate file path for new post category image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'postCategory', filename)


def post_image_file_path(instance, filename):
    """Generate file path for new post image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'post', filename)


class PostCategory(AuditModel):
    """post category objects"""
    title = models.CharField(max_length=100, unique=True)
    parentPostCategoryId = models.ForeignKey('self',
                                             on_delete=models.CASCADE,
                                             null=True,
                                             blank=True,
                                             related_name='children')
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=False,
                              blank=True,
                              default="",
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

    class Meta:
        verbose_name = "Post Category"
        verbose_name_plural = "Post Categories"

    def __str__(self):
        return self.title


class PostQuerySet(models.QuerySet):
    def high_rated(self):
        return self.annotate(
            avg_rating=Avg(
                'postInformation__averageRating')).filter(avg_rating__gte=4)

    def accepted(self):
        return self.filter(reviewStatus='accept')

    def published(self):
        return self.filter(postStatus='publish')

class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def published_and_accepted(self):
        return self.get_queryset().published().accepted()

    def get_random_high_rated_posts(self, count):
        high_rated_posts = self.get_queryset().published().high_rated().accepted()

        # Ensure the count does not exceed the number of available posts
        if count > high_rated_posts.count():
            count = high_rated_posts.count()
        return random.sample(list(high_rated_posts), count)


class Post(AuditModel):
    """Post objects"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('publish', 'Publish'),
        ('archive', 'Archive'),
    ]

    REVIEW_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accept', 'Accept'),
        ('reject', 'Reject'),
    ]
    title = models.CharField(
        max_length=100,
        unique=False,
        verbose_name="Post Title")
    content = CKEditor5Field(
        config_name='extends')
    postCategoryId = models.ForeignKey(
        PostCategory,
        null=False,
        blank=False,
        verbose_name="Post Category",
        on_delete=models.RESTRICT
        )
    image = models.ImageField(
        null=False,
        blank=True,
        upload_to=post_image_file_path,
        default="",
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
    reviewStatus = models.CharField(
        max_length=10,
        choices=REVIEW_STATUS_CHOICES,
        default='pending',
        verbose_name="Review Status"
    )
    reviewResponseDate = models.DateTimeField(
        null=True,
        verbose_name="Review Response Date"
        )
    isExternalSource = models.BooleanField(
        verbose_name="Is External Source",
        default=False)
    externalLink = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="External link")
    commentsEnabled = models.BooleanField(
        null=False,
        blank=False,
        default=True,
        verbose_name="Enable Comments")
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
    excerpt = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name="Excerpt",
        help_text="""
        Provides a short summary or teaser of the blog post,
        displayed on archive pages or in search results.
        """
    )
    relatedPosts = models.ManyToManyField(
        'self',
        blank=True
        )

    objects = PostManager()
    
    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def _can_change_postStatus(self, new_status):
        if self.postStatus == 'draft' and new_status in ['draft',
                                                         'publish']:
            return True
        elif self.postStatus == 'publish' and new_status in ['publish',
                                                             'archive']:
            return True
        return False

    def change_postStatus_to(self, new_status):
        if self._can_change_postStatus(new_status):
            self.postStatus = new_status
            self.save()
        else:
            raise ValueError(
                f"""
                Cannot change post status of {self.title} from
                {self.postStatus} to {new_status}
                """
                )

    def _can_change_reviewStatus(self, new_status):
        if self.postStatus in ['draft', 'archive']:
            raise ValueError(
                f"""
                Cannot change review status of {self.title} because
                it is not published yet.
                """
                )
        if self.reviewStatus == 'pending' and new_status in ['pending',
                                                             'accept',
                                                             'reject']:
            return True
        elif self.reviewStatus == 'accept' and new_status in ['accept',
                                                              'reject']:
            return True
        elif self.reviewStatus == 'reject' and new_status in ['reject',
                                                              'accept']:
            return True
        return False

    def change_reviewStatus_to(self, new_status):
        if self._can_change_reviewStatus(new_status):
            self.reviewStatus = new_status
            self.reviewResponseDate = timezone.now()
            self.save()
        else:
            raise ValueError(
                f"""
                Cannot change review status of {self.title} from
                {self.reviewStatus} to {new_status}
                """
                )

    def clean(self):
        super().clean()
        if self.isExternalSource and not self.externalLink:
            raise ValidationError(
                "External link must be provided for posts from external sources.")  # noqa

    def __str__(self):
        return self.title


class Tag(AuditModel):
    """Tags for filtering posts."""
    name = models.CharField(max_length=255)
    isDeleted = models.BooleanField(
        default=False,
        verbose_name="Is Deleted"
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class SEOKeywords(AuditModel):
    """SEO keywrods for the posts."""
    keyword = models.CharField(max_length=255)

    class Meta:
        verbose_name = "SEO Keyword"
        verbose_name_plural = "SEO Keywords"

    def __str__(self):
        return self.keyword


class PostInformation(models.Model):
    """Post Detail objects"""
    post = models.OneToOneField(
        'Post',
        on_delete=models.CASCADE,
        related_name='postInformation'
    )
    viewCount = models.PositiveIntegerField(
        help_text="""
        Tracks the number of views or visits the blog post has received.
        """,
        null=True,
        blank=True,
        default=0
    )
    socialShareCount = models.PositiveIntegerField(
        help_text="""
        Tracks the number of times the blog post has been shared
        on social media platforms.
        """,
        null=True,
        blank=True,
        default=0
    )
    ratingCount = models.PositiveIntegerField(
        help_text="""
        Tracks the number of user ratings received for the blog post.
        """,
        null=True,
        blank=True,
        default=0
    )
    averageRating = models.FloatField(
        help_text="""
        Calculates the average rating score based on user ratings,
        providing feedback on content quality.
        """,
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(5)
        ]
    )
    commentCount = models.IntegerField(
        help_text="""
        Counts the number of comments posted on the blog post,
        fostering community interaction and discussion.
        """,
        null=True,
        blank=True,
        default=0
    )

    def increment_view_count(self):
        self.viewCount += 1
        self.save()

    def increment_social_share_count(self):
        self.socialShareCount += 1
        self.save()

    class Meta:
        verbose_name = 'Post Information'
        verbose_name_plural = 'Posts Information'


class PostRate(models.Model):
    """Rating For Posts"""
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="%(class)s_user"
    )
    rate = models.PositiveIntegerField(
        null=False,
        blank=False,
        help_text="must be one of these: 1,2,3,4,5",
        validators=[
            MaxValueValidator(5)
        ]
    )

    class Meta:
        unique_together = ('user', 'post',)
