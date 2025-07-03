from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, UploadedFile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role')
    list_select_related = ('profile', )

    def get_role(self, instance):
        return instance.profile.get_role_display()
    get_role.short_description = 'Role'

class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at', 'uploaded_by')
    search_fields = ('original_filename', 'uploaded_by__username')
    readonly_fields = ('uploaded_at',)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UploadedFile, UploadedFileAdmin)
