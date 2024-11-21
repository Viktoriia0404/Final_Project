from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied





class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj.owner == request.user  # Make sure this matches the correct field in the Booking model


class IsNotOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj.owner != request.user


class IsNotLandlordForCreate(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method == 'POST':
            return not getattr(request.user, 'is_landlord', False)
        return True
