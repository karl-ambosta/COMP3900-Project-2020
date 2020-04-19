from rest_framework import permissions
from .models import UserProfile
#from django.db import models
from .models import UserProfile, MenuItem, MenuCategory, OrderList, OrderRequest, Restaurant, OpeningHours
from django.contrib.auth.models import User

class IsUser(permissions.BasePermission): 
    def has_object_permission(self, request, view, obj):
        if request.user:
            if request.user.is_superuser:
                return True
            else:
                return obj.username == request.user.username
        else:
            return False

class IsCustomer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if (UserProfile.objects.get(user=request.user).role) == '1':
            return True
        else: 
            return False

class IsCashier(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if (UserProfile.objects.get(user=request.user).role) == '2':
            return True

class IsKitchen(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if (UserProfile.objects.get(user=request.user).role) == '3':
            return True
  
class IsManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if (UserProfile.objects.get(user=request.user).role) == '4':
            return True

class IsWaiter (permissions.BasePermission): 
    def has_object_permission(self, request, view, obj):
        if (UserProfile.objects.get(user=request.user).role) == '5':
            return True


class MenuItemPermissions(permissions.BasePermission): 
    def has_permission(self, request, view):
        if view.action == 'create': 
            return ((UserProfile.objects.get(user=request.user).role) == '3') or ((UserProfile.objects.get(user=request.user).role) == '4')          
        elif view.action == 'list':
            return True

        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        #if not request.user.is_authenticated():
        #    return False
        if view.action == 'retrieve':
            return IsCustomer()
            #return obj == request.user or request.user.is_admin
        elif view.action in ['update', 'partial_update']:
            print(IsCustomer())
            if IsCustomer(): 
                print ("lol")
                return True
            #return obj == request.user or request.user.is_admin
        elif view.action == 'destroy':
            return request.user.is_staff
        else:
            return False