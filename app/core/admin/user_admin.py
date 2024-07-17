from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group



class UserAdmin(BaseUserAdmin):
    """Define the admin page for users."""
    # list of users page
    ordering = ['id']
    list_display = ['email', 'name', 'image']
    list_filter = ['is_activate', 'is_staff']
    search_fields = ['email', 'name']
    # edit user page
    fieldsets = (
        (
            _('Credentials'),
            {'fields': ('email', 'password',)}
        ),
        (
            _('Personal Information'),
            {'fields': ('name', 'image')}
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
                'image'
            ),
        }),
    )

User = get_user_model()


# Create ModelForm based on the Group model.
class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = []

    # Add the users field.
    users = forms.ModelMultipleChoiceField(
         queryset=User.objects.all(),
         required=False,
         # Use the pretty 'filter_horizontal widget'.
         widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        # Default save
        instance = super(GroupAdminForm, self).save()
        # Save many-to-many data
        self.save_m2m()
        return instance


# Unregister the original Group admin.
admin.site.unregister(Group)


class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']


# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)

admin.site.register(models.User, UserAdmin)
