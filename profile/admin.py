from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class ProfileUserAdmin(UserAdmin):
    inlines = (ProfileInline, )


    def get_queryset(self, request):
        '''Let common users only edit their own profile'''
        if not request.user.is_superuser:
            return super(UserAdmin, self).get_queryset(request).filter(pk=request.user.id)

        return super(UserAdmin, self).get_queryset(request)

    def get_readonly_fields(self, request, obj=None):
        '''Limit field access for common users'''
        if not request.user.is_superuser:
            return ('username', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login', 'groups', 'user_permissions')
        return list()

    def get_inline_instances(self, request, obj=None):
        '''Append profile fields to UserAdmin'''
        if not obj:
            return list()

        return super(ProfileUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, ProfileUserAdmin)