from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
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


admin.site.register(models.User, UserAdmin)