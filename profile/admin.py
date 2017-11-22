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
        # Users can only edit their own profile
        if not request.user.is_superuser:
            return super(UserAdmin, self).get_queryset(request).filter(pk=request.user.id)

        return super(UserAdmin, self).get_queryset(request)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(ProfileUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, ProfileUserAdmin)