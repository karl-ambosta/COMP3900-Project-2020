from rest_framework import permissions
from .models import UserProfile
#from django.db import models
from .models import UserProfile, MenuItem, MenuCategory, OrderList, OrderRequest, Restaurant, OpeningHours
from django.contrib.auth.models import User

'''
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user
'''
'''
class IsSuperUser(permissions.BasePermission): 
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
'''

class IsUser(permissions.BasePermission): 
    def has_object_permission(self, request, view, obj):
        if request.user:
            #print(request.user.username)
            #print(obj.username)
            if request.user.is_superuser:
                return True
            else:
                return obj.username == request.user.username
        else:
            return False

class IsCustomer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        #print(UserProfile.objects.get(pk=view.kwargs['pk']).role)
        if UserProfile.objects.get(pk=view.kwargs['pk']).role == '1':
            return True

class IsCashier(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if UserProfile.objects.get(pk=view.kwargs['pk']).role == '2':
            return True

class IsKitchen(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if UserProfile.objects.get(pk=view.kwargs['pk']).role == '3':
            return True
  
class IsManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if UserProfile.objects.get(pk=view.kwargs['pk']).role == '4':
            return True

class IsWaiter (permissions.BasePermission): 
    def has_object_permission(self, request, view, obj):
        if UserProfile.objects.get(pk=view.kwargs['pk']).role == '5':
            return True



