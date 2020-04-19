from rest_framework import permissions
from .models import UserProfile
#from django.db import models
from .models import UserProfile, MenuItem, MenuCategory, OrderList, OrderRequest, Restaurant, OpeningHours
from django.contrib.auth.models import User

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user

class IsCustomer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.role == '1'

class IsCashier(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.role == '2'

class IsKitchen(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.role == '3'

class IsManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.role == '4'




