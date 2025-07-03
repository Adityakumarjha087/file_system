from rest_framework import permissions

class IsOpsUser(permissions.BasePermission):
    """
    Allows access only to users with 'ops' role.
    """
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'ops')

class IsClientUser(permissions.BasePermission):
    """
    Allows access only to users with 'client' role.
    """
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'client')
