from django.contrib.auth.models import User
from .models import MenuItem, MenuCategory
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class MenuItemSerializer(serializers.HyperlinkedModelSerializer): 
    class Meta:
        model = MenuItem
        fields = ['name', 'price']

class MenuCategorySerializer(serializers.HyperlinkedModelSerializer):
    menuItem = serializers.ReadOnlyField(source='menuItem.name')
    class Meta:
        model = MenuCategory
        fields = ['name', 'menuItem']
