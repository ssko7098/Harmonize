from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


# Register your models here.
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    search_fields = ('email', 'username')
    list_filter = ('email', 'username', 'is_active', 'is_admin')
    list_display = ('email', 'username', 'is_active', 'is_admin')

    fieldsets = (
    (None, {'fields': ('email', 'username',)}),
    ('Permissions', {'fields': ('is_admin', 'is_active')}),
    )
    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': ('email', 'username', 'password', 'is_active', 'is_admin')
            }
        ),
    )

    ordering = ('date_joined',)

admin.site.register(User, UserAdmin)
