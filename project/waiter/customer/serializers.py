from django.contrib.auth.models import User
from .models import UserProfile, MenuItem, MenuCategory, OrderList, OrderRequest, Restaurant, OpeningHours, WaiterCalls
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'url','first_name', 'last_name','username','email', 'is_staff']

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source = "user.username",read_only=True)
    email = serializers.EmailField (source="user.email",read_only=True)
    
    class Meta: 
        model = UserProfile
        fields = ('__all__')

class RestaurantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'opening_hours']

class MenuCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'menu_item', 'restaurant', 'order']

class MenuItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'description', 'menu_category', 'picture', 'order', 'active']

class OrderListSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    order_total = serializers.DecimalField(decimal_places=2, max_digits=9, read_only=True)
    status = serializers.ReadOnlyField()

    class Meta:
        model = OrderList
        fields = ['id', 'owner', 'order_request', 'restaurant', 'order_total', 'table_number', 'status', 'owner_id', 'created_at', 'updated_at']

class OrderRequestSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    total = serializers.DecimalField(decimal_places=2, max_digits=9, read_only=True)

    class Meta:
        model = OrderRequest
        fields = ['id', 'order_list', 'owner', 'menu_item', 'comments', 'quantity', 'total', 'created_at', 'updated_at']

class OpeningHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningHours
        fields = ['id', 'restaurant', 'day', 'from_hour', 'to_hour']

class WaiterCallsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaiterCalls
        fields = ['id', 'table_number', 'caller', 'status']