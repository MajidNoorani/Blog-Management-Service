from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Post, PostInformation


@receiver(post_save, sender=Post)
def create_post_information(sender, instance, created, **kwargs):
    if created:
        PostInformation.objects.create(post=instance)
