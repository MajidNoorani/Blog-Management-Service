from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from core.models import CommentReaction


@receiver(pre_save, sender=CommentReaction)
def detect_reaction_change(sender, instance, **kwargs):
    if instance.pk:
        previous = CommentReaction.objects.get(pk=instance.pk)
        if previous.reaction != instance.reaction:
            instance.previous_reaction = previous.reaction
        else:
            instance.previous_reaction = None
    else:
        instance.previous_reaction = None


@receiver(post_save, sender=CommentReaction)
def update_comment_reaction_counts_on_save(sender,
                                           instance,
                                           created,
                                           **kwargs):
    comment = instance.comment
    if created or instance.previous_reaction:
        comment.likeCount = CommentReaction.objects.filter(
            comment=comment,
            reaction='like'
            ).count()
        comment.disLikeCount = CommentReaction.objects.filter(
            comment=comment,
            reaction='disLike'
            ).count()
        comment.save()


@receiver(post_delete, sender=CommentReaction)
def update_comment_reaction_counts_on_delete(sender, instance, **kwargs):
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
