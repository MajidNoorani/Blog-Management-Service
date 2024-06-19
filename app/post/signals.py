from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from core.models import Post, PostInformation, Comment, PostRate


@receiver(post_save, sender=Post)
def create_post_information(sender, instance, created, **kwargs):
    if created:
        PostInformation.objects.create(post=instance)


@receiver(post_save, sender=Comment)
def update_comment_counts_on_save(sender, instance, created, **kwargs):
    if created:
        post_information = instance.post.postInformation
        post_information.commentCount = Comment.objects.filter(
            post=instance.post
        ).count()
        post_information.save()


@receiver(post_delete, sender=Comment)
def update_comment_counts_on_delete(sender, instance, **kwargs):
    post_information = instance.post.postInformation
    post_information.commentCount = Comment.objects.filter(
        post=instance.post
    ).count()
    post_information.save()


@receiver(pre_save, sender=PostRate)
def detect_rate_change(sender, instance, **kwargs):
    if instance.pk:
        previous = PostRate.objects.get(pk=instance.pk)
        if previous.rate != instance.rate:
            instance.previous_rate = previous.rate
        else:
            instance.previous_rate = None
    else:
        instance.previous_rate = None


@receiver([post_save, post_delete], sender=PostRate)
def update_averageRating(sender, instance, **kwargs):
    post = instance.post.postInformation
    # Calculate the average rating for the associated post
    average_rating = PostRate.objects.filter(
        post=instance.post
        ).aggregate(Avg('rate'))['rate__avg']
    post.ratingCount = PostRate.objects.filter(
        post=instance.post
        ).count()

    # Update the averageRating field in the related postInformation model
    if average_rating is not None:
        post.averageRating = round(average_rating, 2)
    else:
        post.averageRating = 0.0

    post.save()
