from django.contrib.auth.models import User
from .models import MenuItem, MenuCategory
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class MenuCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'menu_item']

class MenuItemSerializer(serializers.HyperlinkedModelSerializer): 
    menu_category = serializers.ReadOnlyField(source='menu_category.id')
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'description', 'menu_category']