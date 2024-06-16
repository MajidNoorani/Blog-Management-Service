from django.db import models
from django.conf import settings


class Comment(models.Model):
    """Comment objects for posts"""
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        null=False,
        blank=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="%(class)s_user"
    )
    parentComment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comment_reply')
    comment = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )
    likeCount = models.PositiveIntegerField(
        help_text="""
        Records the number of likes or thumbs-up the comment has received.
        """,
        null=True,
        blank=True,
        default=0
    )
    disLikeCount = models.PositiveIntegerField(
        help_text="""
        Records the number of dislikes or thumbs-down the comment has received.
        """,
        null=True,
        blank=True,
        default=0
    )


class CommentReaction(models.Model):
    """Comment Reactions by users"""
    REACTION_CHOICE = [
        ('like', 'Like'),
        ('disLike', 'DisLike')
    ]

    comment = models.ForeignKey(
        'Comment',
        on_delete=models.CASCADE,
        null=False,
        blank=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="%(class)s_user"
    )
    reaction = models.CharField(
        max_length=7,
        choices=REACTION_CHOICE,
        verbose_name="Review Status"
    )

    class Meta:
        unique_together = ('comment', 'user',)
