from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django.utils import timezone

from core import models


class PostCategoryAdmin(admin.ModelAdmin):
    """Define the admin page for postCategories."""
    # list of postCategories page
    ordering = ['id']
    list_display = ['title', 'parentPostCategoryId', 'description',
                    'status', 'updatedDate', 'image']
    # filters and search
    list_filter = ['status']
    search_fields = ['title',
                     'parentPostCategoryId__title',
                     'createdBy__email',
                     'updatedBy__email']
    # edit postCategories page
    fieldsets = (
        (
            _('General Information'),
            {'fields': (
                'title', 'parentPostCategoryId', 'description', 'image',
                )}
        ),
        (
            _('Status'),
            {'fields': ('status',)}
        ),
        (
            _('Audit Information'),
            {'fields': (
                'createdBy', 'createdDate', 'updatedBy', 'updatedDate',
                )}
        ),
    )
    readonly_fields = ['createdBy', 'createdDate', 'updatedBy', 'updatedDate']
    # Add post category page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'parentPostCategoryId', 'description',
                       'image', 'status', 'createdBy', 'createdDate',
                       'updatedBy', 'updatedDate'),
        }),
    )

    # enable save as new button on update
    save_as = True

    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically assign the current user
        to createdBy and updatedBy fields.
        """
        if not change:  # Only update the fields when creating a new object
            obj.createdBy = request.user
            obj.updatedBy = request.user
        else:  # For updating existing objects
            obj.updatedBy = request.user
            obj.updatedDate = timezone.now()
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


class TagInline(admin.TabularInline):
    model = models.Post.tags.through
    extra = 1  # Number of extra forms to display
    verbose_name = "Tag"
    verbose_name_plural = "Tags"


class SEOKeywordsInline(admin.TabularInline):
    model = models.Post.seoKeywords.through
    extra = 1  # Number of extra forms to display
    verbose_name = "SEO Keyword"
    verbose_name_plural = "SEO Keywords"


class RelatedPostInline(admin.TabularInline):
    model = models.Post.relatedPosts.through
    fk_name = 'from_post'
    extra = 1  # Number of extra forms to display
    verbose_name = "Related Post"
    verbose_name_plural = "Related Posts"


class PostAdmin(admin.ModelAdmin):
    """Define the admin page for posts."""
    # list of postCategories page
    ordering = ['-updatedDate', 'title']
    list_display = ['title', 'postStatus', 'postCategoryId',
                    'display_tags',
                    'image', 'updatedDate', 'updatedBy']
    # filters and search
    list_filter = ['postStatus']
    search_fields = ['title',
                     'postCategoryId__title',
                     'createdBy__email',
                     'updatedBy__email']
    # edit postCategories page
    fieldsets = (
        (
            _('General Information'),
            {'fields': (
                'title', 'postCategoryId', 'content', 'image',
                'isExternalSource', 'externalLink',
                'readTime', 'metaDescription'
                )}
        ),
        (
            _('Status'),
            {'fields': ('postStatus',)}
        ),
        (
            _('Comments'),
            {'fields': ('commentsEnabled',)}
        ),
        # (
        #     _('Extra Information'),
        #     {'fields': ('relatedPosts',)}
        # ),
        (
            _('Audit Information'),
            {'fields': (
                'createdBy', 'createdDate', 'updatedBy', 'updatedDate',
                'postPublishDate', 'postArchivedDate'
                )}
        ),


    )
    readonly_fields = ['createdBy', 'createdDate', 'updatedBy', 'updatedDate',
                       'postPublishDate', 'postArchivedDate', 'postStatus']
    # Add post category page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'postCategoryId', 'content', 'image',
                       'display_tags', 'isExternalSource', 'externalLink',
                       'readTime', 'metaDescription', 'postStatus',
                       'commentsEnabled', 'display_seokeywords',
                       'relatedPosts', 'createdBy', 'createdDate', 'updatedBy',
                       'updatedDate', 'postPublishDate', 'postArchivedDate'),
        }),
    )

    inlines = [
        TagInline, SEOKeywordsInline, RelatedPostInline
    ]

    # enable save as new button on update
    save_as = True

    def display_seokeywords(self, obj):
        """Create a string representation of the tags."""
        return ", ".join(
            seokeyword.keyword for seokeyword in obj.seokeywords.all()
            )
    display_seokeywords.short_description = 'SEO Keywords'

    def display_tags(self, obj):
        """Create a string representation of the tags."""
        return ", ".join(tag.name for tag in obj.tags.all())
    display_tags.short_description = 'Tags'

    def display_relatedPosts(self, obj):
        """Create a string representation of the tags."""
        return ", ".join(post.title for post in obj.relatedPosts.all())
    display_relatedPosts.short_description = 'related Posts'

    actions = ['make_draft', 'make_publish', 'make_archive']

    def make_draft(self, request, queryset):
        for post in queryset:
            try:
                post.change_to('draft')
            except ValueError as e:
                self.message_user(request, f"Error: {e}", level='ERROR')
    make_draft.short_description = 'Mark selected posts as Draft'

    def make_publish(self, request, queryset):
        for post in queryset:
            try:
                post.change_to('publish')
            except ValueError as e:
                self.message_user(request, f"Error: {e}", level='ERROR')
    make_publish.short_description = 'Mark selected posts as Publish'

    def make_archive(self, request, queryset):
        for post in queryset:
            try:
                post.change_to('archive')
            except ValueError as e:
                self.message_user(request, f"Error: {e}", level='ERROR')
    make_archive.short_description = 'Mark selected posts as Archive'

    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically assign the current user
        to createdBy and updatedBy fields.
        """
        if not change:  # Only update the fields when creating a new object
            obj.createdBy = request.user
            obj.updatedBy = request.user
        else:  # For updating existing objects
            obj.updatedBy = request.user
            obj.updatedDate = timezone.now()

            # Update the postPublishDate if status is changed to 'publish'
            if obj.postStatus == 'publish' and 'postStatus' in form.changed_data:
                obj.postPublishDate = timezone.now()

            # Update the postArchivedDate if status is changed to 'archive'
            if obj.postStatus == 'archive' and 'postStatus' in form.changed_data:
                obj.postArchivedDate = timezone.now()

        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'updatedBy']
    search_fields = ['name', 'updatedBy__email']
    readonly_fields = ['createdBy', 'createdDate', 'updatedBy', 'updatedDate']

    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically assign the current user
        to createdBy and updatedBy fields.
        """
        if not change:  # Only update the fields when creating a new object
            obj.createdBy = request.user
            obj.updatedBy = request.user
        else:  # For updating existing objects
            obj.updatedBy = request.user
            obj.updatedDate = timezone.now()

        super().save_model(request, obj, form, change)


class SEOKeywordsAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'updatedBy']
    search_fields = ['keyword', 'updatedBy__email']
    readonly_fields = ['createdBy', 'createdDate', 'updatedBy', 'updatedDate']

    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically assign the current user
        to createdBy and updatedBy fields.
        """
        if not change:  # Only update the fields when creating a new object
            obj.createdBy = request.user
            obj.updatedBy = request.user
        else:  # For updating existing objects
            obj.updatedBy = request.user
            obj.updatedDate = timezone.now()

        super().save_model(request, obj, form, change)


admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.SEOKeywords, SEOKeywordsAdmin)
admin.site.register(models.PostCategory, PostCategoryAdmin)
admin.site.register(models.Post, PostAdmin)
