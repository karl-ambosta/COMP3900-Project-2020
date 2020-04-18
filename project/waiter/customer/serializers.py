from django.contrib.auth.models import User
from .models import UserProfile, MenuItem, MenuCategory, OrderList, OrderRequest, Restaurant, OpeningHours
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['url','username', 'email', 'is_staff']

        def create(self, validated_data):
            profile_data = validated_data.pop('profile')
            user = User.objects.create(**validated_data)
            UserProfile.objects.create(**profile_data)
            return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        # Update User data 
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('first_name', instance.email)
        # Update UserProfile data
        if not instance.profile:
            UserProfile.objects.create(user=instance, **profile_data)
        instance.profile.first_name = profile_data.get('first_name', instance.profile.first_name)
        instance.profile.last_name = profile_data.get('first_name', instance.profile.last_name)
        instance.profile.uid = profile_data.get('uid', instance.profile.uid)
        instance.profile.phone = profile_data.get('uid', instance.profile.phone)
        #instance.profile.cell_phone = profile_data.get('uid', instance.profile.cell_phone)
        instance.save()
        # Check if the password has changed
        password = validated_data.get('password', None)
        confirm_password = validated_data.get('confirm_password', None)

        if password and confirm_password and password == confirm_password:
            instance.set_password(password)
            instance.save()
            update_session_auth_hash(self.context.get('request'), instance)

        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        #fields = ['id','name', 'email','created']


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

    class Meta:
        model = OrderList
        fields = ['id', 'owner', 'order_request', 'restaurant', 'order_total', 'table_number', 'status']

class OrderRequestSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    total = serializers.DecimalField(decimal_places=2, max_digits=9, read_only=True)

    class Meta:
        model = OrderRequest
        fields = ['id', 'order_list', 'owner', 'menu_item', 'comments', 'quantity', 'total']

class OpeningHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningHours
        fields = ['id', 'restaurant', 'day', 'from_hour', 'to_hour']