from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core import models


class CommentReactionInline(admin.TabularInline):
    model = models.CommentReaction
    extra = 1  # Number of extra forms to display
    verbose_name = "Comment Reaction"
    verbose_name_plural = "Comment Reactions"


class CommentAdmin(admin.ModelAdmin):
    """Define the admin page for Organization."""
    ordering = ['-createdDate']
    list_display = ['id', 'comment', 'parentComment', 'user', 'isDeleted']

    search_fields = ['comment', 'user']
    list_filter = ['isDeleted']
    # edit Organization page
    fieldsets = (
        (
            _('General Fields'),
            {'fields': (
                'post', 'comment', 'user', 'parentComment'
                )}
        ),
        (
            _('Reaction Status'),
            {'fields': (
                'likeCount', 'disLikeCount'
                )}
        ),
        (
            _('Important Dates'),
            {'fields': (
                'createdDate',
                )}
        ),
        (
            _('Statuss'),
            {'fields': (
                'isDeleted',
                )}
        ),

    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('organization', 'comment', 'likeCount',
                       'disLikeCount', 'starRate'),
        }),
    )

    readonly_fields = ["createdDate", 'user', 'likeCount', 'disLikeCount']

    inlines = [CommentReactionInline]

    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically assign the current user
        to createdBy and updatedBy fields.
        """
        if not change:  # Only update the fields when creating a new object
            obj.user = request.user

        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


class CommentReactionAdmin(admin.ModelAdmin):
    """Define the admin page for Organization."""
    ordering = ['id']
    list_display = ['comment', 'user', 'reaction']

    list_filter = ['reaction']

    search_fields = ['comment', 'user']

    # edit Organization page
    fieldsets = (
        (
            _('General Fields'),
            {'fields': (
                'comment', 'user',
                )}
        ),
        (
            _('Reaction Status'),
            {'fields': (
                'reaction',
                )}
        ),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('organization', 'comment', 'reaction'),
        }),
    )


admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.CommentReaction, CommentReactionAdmin)
