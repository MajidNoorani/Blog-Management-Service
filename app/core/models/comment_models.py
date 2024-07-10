from django.db import models
from django.conf import settings
from django.utils import timezone


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
    createdDate = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created Date"
        )
    isDeleted = models.BooleanField(
        default=0,
        verbose_name="Is Deleted"
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def _can_delete_comment(self, new_delete_status):
        if self.isDeleted == 0 and new_delete_status == 1:
            return True
        return False

    def delete_comment(self, new_delete_status):
        if self._can_delete_comment(new_delete_status):
            self.isDeleted = new_delete_status
            self.save()
        else:
            raise ValueError(
                f"""
                Cannot change delete status of {self.comment} from
                {self.isDeleted} to {new_delete_status}
                """
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
