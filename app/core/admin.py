"""Customizing django admin"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Recipie, Tag, Ingredient
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    ordering = ('id',)
    list_display = ('email', 'name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _("Permissions"), {
                'fields': (
                    'is_active',
                    'is_superuser',
                    'is_staff'
                )
            }
        ),
        (_('Important dates'), {
            'fields': ('last_login',)
        })

    )
    readonly_fields = ('last_login',)
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': {
                    'email',
                    'password1',
                    'password2',
                    'name',
                    'is_active',
                    'is_superuser'
                }

            }
        ),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Recipie)
admin.site.register(Tag)
admin.site.register(Ingredient)
