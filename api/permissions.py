from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Only admin users."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )

class IsAnalystOrAdmin(BasePermission):
    """Analyst or admin users."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('analyst', 'admin')
        )

class IsAnyAuthenticatedRole(BasePermission):
    """Any authenticated user (viewer, analyst, admin)."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
