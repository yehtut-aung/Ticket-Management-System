from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role')
    
    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Role'

# Unregister default User admin and register custom
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)