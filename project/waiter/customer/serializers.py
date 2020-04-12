from django.contrib.auth.models import User
from .models import MenuItem, MenuCategory, OrderList, OrderRequest, Restaurant, OpeningHours
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'email']

class RestaurantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description']

class MenuCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'menu_item', 'restaurant']

class MenuItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'description', 'menu_category']

class OrderListSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = OrderList
        fields = ['id', 'owner', 'order_request', 'restaurant']

class OrderRequestSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = OrderRequest
        fields = ['id', 'order_list', 'owner', 'menu_item', 'comments', 'quantity']

class OpeningHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningHours
        fields = ['id', 'restaurant', 'day', 'from_hour', 'to_hour']