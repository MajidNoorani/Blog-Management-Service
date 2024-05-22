from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from django.utils import timezone

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin page for users."""
    # list of users page
    ordering = ['id']
    list_display = ['email', 'name',]
    list_filter = ['is_activate', 'is_staff']
    # edit user page
    fieldsets = (
        (
            _('Credentials'),
            {'fields': ('email', 'password',)}
        ),
        (
            _('Personal Information'),
            {'fields': ('name',)}
        ),
        (
            _('Permissions'),
            {'fields': ('is_activate',
                        'is_staff',
                        'is_superuser',)}
        ),
        (
            _('Important Dates'),
            {'fields': ('last_login', 'date_joined',)}
        ),
    )
    readonly_fields = ['last_login', 'date_joined']
    # add user page
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),  # this only changes the page UI
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_activate',
                'is_staff',
                'is_superuser',
            ),
        }),
    )


class PostCategoryAdmin(admin.ModelAdmin):
    """Define the admin page for postCategories."""
    # list of postCategories page
    ordering = ['id']
    list_display = ['title', 'parentPostCategoryId', 'description',
                    'status', 'createdBy', 'createdDate', 'updatedBy',
                    'updatedDate', 'image']
    list_filter = ['status']
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

    # def save_formset(self, request, form, formset, change):
    #     """Override save_formset to handle updating related objects."""
    #     instances = formset.save(commit=False)
    #     for obj in formset.deleted_objects:
    #         obj.delete()
    #     for instance in instances:
    #         if isinstance(instance, models.PostCategory):
    #             # Check if it's an instance of PostCategory
    #             instance.updatedBy = request.user
    #             instance.updatedDate = timezone.now()
    #             instance.save()
    #     formset.save_m2m()


admin.site.register(models.User, UserAdmin)
admin.site.register(models.PostCategory, PostCategoryAdmin)
