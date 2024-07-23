from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django.utils import timezone

from core import models
from django.utils.safestring import mark_safe

from django.urls import reverse
from django.utils.html import format_html


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
    list_display = ['id', 'title', 'postStatus', 'postCategoryId',
                    'reviewStatus', 'display_tags',
                    'createdDate', 'postPublishDate', 'reviewResponseDate',
                    'createdBy', 'post_information_link']
    # filters and search
    list_filter = ['postStatus', 'reviewStatus']
    search_fields = ['title',
                     'postCategoryId__title',
                     'createdBy__email',
                     'updatedBy__email']
    # edit Posts page
    fieldsets = (
        (
            _('General Information'),
            {'fields': (
                'id', 'title', 'postCategoryId', 'content', 'image',
                'isExternalSource', 'externalLink',
                'readTime', 'excerpt',
                )}
        ),
        (
            _('Status'),
            {
                'fields': ('reviewStatus', 'postStatus',),
                'description': mark_safe(
                    """
                    <p style="font-size: 12px; color: #872b72;">
                    You can change the Review Status with <strong>Acions</strong>
                    in the list of posts.
                    </p>
                    """
                    )
             }
        ),
        (
            _('Comments'),
            {'fields': ('commentsEnabled',)}
        ),
        (
            _('Audit Information'),
            {'fields': (
                'createdBy', 'createdDate', 'updatedBy', 'updatedDate',
                'postPublishDate', 'postArchivedDate', 'reviewResponseDate'
                )}
        ),
        (
            _('SEO'),
            {'fields': ('metaDescription',)}
        ),
    )

    readonly_fields = ['id', 'createdBy', 'createdDate', 'updatedBy',
                       'updatedDate', 'postPublishDate', 'postArchivedDate',
                       'reviewStatus', 'reviewResponseDate']
    # Add post page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'postCategoryId', 'content', 'image',
                       'display_tags', 'isExternalSource', 'externalLink',
                       'readTime', 'metaDescription', 'postStatus',
                       'reviewStatus', 'commentsEnabled', 'excerpt',
                       'display_seokeywords',
                       'relatedPosts', 'createdBy', 'createdDate', 'updatedBy',
                       'updatedDate', 'postPublishDate', 'postArchivedDate',
                       'reviewResponseDate'),
        }),
    )

    inlines = [
        SEOKeywordsInline, TagInline, RelatedPostInline
    ]

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(PostAdmin, self).get_form(request, obj, **kwargs)
    #     form.base_fields['content'].widget.attrs['style'] = 'width: 45em;'
    #     return form

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
        return ", ".join(
            tag.name for tag in obj.tags.all()
            )
    display_tags.short_description = 'Tags'

    def display_relatedPosts(self, obj):
        """Create a string representation of the tags."""
        return ", ".join(
            post.title for post in obj.relatedPosts.all()
            )
    display_relatedPosts.short_description = 'Related Posts'

    actions = ['make_accepted', 'make_rejected', 'delete']

    # def make_draft(self, request, queryset):
    #     for post in queryset:
    #         try:
    #             post.change_to('draft')
    #         except ValueError as e:
    #             self.message_user(request, f"Error: {e}", level='ERROR')
    # make_draft.short_description = 'Mark selected posts as Draft'

    def make_accepted(self, request, queryset):
        for post in queryset:
            try:
                post.change_reviewStatus_to('accept')
            except ValueError as e:
                self.message_user(request, f"Error: {e}", level='ERROR')
    make_accepted.short_description = 'Accept'

    def make_rejected(self, request, queryset):
        for post in queryset:
            try:
                post.change_reviewStatus_to('reject')
            except ValueError as e:
                self.message_user(request, f"Error: {e}", level='ERROR')
    make_rejected.short_description = 'Reject'

    def delete(self, request, queryset):
        for post in queryset:
            try:
                post.delete()
            except ValueError as e:
                self.message_user(request, f"Error: {e}", level='ERROR')
    delete.short_description = 'Delete'

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
            if obj.postStatus == 'publish' and 'postStatus' in form.changed_data:  # noqa
                obj.postPublishDate = timezone.now()

            # Update the postArchivedDate if status is changed to 'archive'
            if obj.postStatus == 'archive' and 'postStatus' in form.changed_data:  # noqa
                obj.postPublishDate = None
                obj.postArchivedDate = timezone.now()

        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False

    def post_information_link(self, obj):
        """Generate a link to the post's information admin page."""
        try:
            post_info = models.PostInformation.objects.get(post=obj)
            url = reverse('admin:core_postinformation_change',
                          args=[post_info.id])
            return format_html('<a href="{}">View Post Information</a>',
                               url)
        except models.PostInformation.DoesNotExist:
            return "No Post Information available"
    post_information_link.short_description = 'Post Information'


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'updatedBy', 'isDeleted']
    search_fields = ['name', 'updatedBy__email']
    readonly_fields = ['createdBy', 'createdDate', 'updatedBy', 'updatedDate']
    list_filter = ['isDeleted']

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


class PostInformationAdmin(admin.ModelAdmin):
    """Define the admin page for PostInformationAdmin."""
    # list of postCategories page
    ordering = ['id']
    list_display = ['post', 'viewCount', 'socialShareCount',
                    'ratingCount', 'averageRating', 'commentCount']
    search_fields = ['post__title']
    # edit postCategories page
    fieldsets = (
        (
            _('Post Analytics'),
            {'fields': (
                'post', 'viewCount', 'socialShareCount', 'ratingCount',
                'averageRating', 'commentCount'
                )}
        ),
    )
    readonly_fields = ['post', 'viewCount', 'socialShareCount', 'ratingCount',
                       'averageRating', 'commentCount']

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.SEOKeywords, SEOKeywordsAdmin)
admin.site.register(models.PostCategory, PostCategoryAdmin)
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.PostInformation, PostInformationAdmin)
