from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import CommentReaction


@receiver([post_save, post_delete], sender=CommentReaction)
def update_comment_reaction_counts_on_save(sender,
                                           instance,
                                           created=False,
                                           **kwargs):
    comment = instance.comment
    comment.likeCount = CommentReaction.objects.filter(
        comment=comment,
        reaction='like'
        ).count()
    comment.disLikeCount = CommentReaction.objects.filter(
        comment=comment,
        reaction='disLike'
        ).count()
    comment.save()
