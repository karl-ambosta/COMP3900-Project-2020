from django.contrib.auth.models import User
from .models import UserProfile, MenuItem, MenuCategory, OrderList, OrderRequest
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = User
        fields = ['url','username', 'email', 'is_staff']

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        #fields = ['id','name', 'email','created']


class MenuCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'menu_item']

class MenuItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'description', 'menu_category']

class OrderListSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = OrderList
        fields = ['id', 'owner', 'order_request']

class OrderRequestSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = OrderRequest
        fields = ['id', 'order_list', 'owner', 'menu_item', 'comments', 'quantity']