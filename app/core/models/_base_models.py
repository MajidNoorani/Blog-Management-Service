
from django.db import models
from django.conf import settings
from django.utils import timezone


class AuditModel(models.Model):
    createdDate = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created Date"
        )
    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="%(class)s_created_by",
        verbose_name="Created By"
    )
    updatedDate = models.DateTimeField(
        default=timezone.now,
        verbose_name="Updated Date"
        )
    updatedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="%(class)s_updated_by",
        verbose_name="Updated By"
    )

    class Meta:
        abstract = True
