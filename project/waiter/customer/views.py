from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions, filters
#from rest_framework import filters
from .serializers import UserSerializer,UserProfileSerializer, MenuItemSerializer, MenuCategorySerializer, OrderListSerializer, OrderRequestSerializer, RestaurantSerializer, OpeningHoursSerializer
from .models import UserProfile, MenuItem, MenuCategory, OrderList, OrderRequest, Restaurant, OpeningHours
from .permissions import IsOwnerOrReadOnly
from rest_framework import permissions
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_framework.decorators import action
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import Http404, HttpResponseBadRequest
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from rest_auth.social_serializers import TwitterLoginSerializer
from django.db.models import Sum, F, DecimalField, ExpressionWrapper


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #permission_classes = [permissions.IsAuthenticated]
   def get_permissions(self):
        # Overrides to tightest security: Only superuser can create, update, partial update, destroy, list
        self.permission_classes = [IsSuperUser]

        # Allow only by explicit exception
        if self.action == 'retrieve':
            self.permission_classes = [IsUser]

        return super(self.__class__, self).get_permissions()    

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_field = 'id'
    lookup_value_regex = '[0-9]+'
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'price', 'menu_category__name']

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    def get_queryset(self):
        qs = MenuItem.objects.all()
        restaurant = self.request.query_params.get('restaurant', None)
        category = self.request.query_params.get('category', None)
        if restaurant is not None:
            qs = qs.filter(menu_category__restaurant__id=restaurant)
        if category is not None:
            qs = qs.filter(menu_category=category)
        return qs
    
    @action(detail=True, methods=['post'])
    def order(self, request, id=None):
        try:
            item = get_object_or_404(self.queryset, id=id)
            owner = get_object_or_404(User.objects.all(), username=self.request.user)
            order_list = get_object_or_404(OrderList.objects.all(), owner=owner)
            if order_list.restaurant.id != item.menu_category.restaurant.id:
                return Response(status=status.HTTP_403_FORBIDDEN)
            order_list.order_request.create(order_list=order_list, owner=owner, menu_item=item, comments=request.data["comments"], quantity=request.data["quantity"])
            return Response(status=status.HTTP_202_ACCEPTED)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def update_order(self, request, id=None):
        try:
            owner = get_object_or_404(User.objects.all(), username=self.request.user)
            order_list = get_object_or_404(OrderList.objects.all(), owner=owner)
            item = get_object_or_404(self.queryset, id=id)
            order_request = get_object_or_404(OrderRequest.objects.all(), owner=owner, order_list=order_list, menu_item=item)
            if request.data["quantity"] == 0:   
                order_request.delete()
                return Response(status=status.HTTP_202_ACCEPTED)
            order_request.quantity = request.data["quantity"]
            order_request.comments = request.data["comments"]
            order_request.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

class MenuCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request): 
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    
    def get_queryset(self):
        qs = MenuCategory.objects.all()
        restaurant = self.request.query_params.get('restaurant', None)
        if restaurant is not None:
            qs = qs.filter(restaurant__id=restaurant)
        return qs


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

class OrderListViewSet(viewsets.ModelViewSet):
    queryset = OrderList.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_204_NO_CONTENT)


class OrderRequestViewSet(viewsets.ModelViewSet):
    queryset = OrderRequest.objects.all()
    serializer_class = OrderRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request): 
        return Response(status=status.HTTP_204_NO_CONTENT)

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request): 
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

class OpeningHoursViewSet(viewsets.ModelViewSet):
    queryset = OpeningHours.objects.all()
    serializer_class = OpeningHoursSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request): 
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
            
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]

    def create(self, request): 
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    basic_auth = False

class GoogleLogin(SocialLoginView):
    adapter_class = CustomGoogleOAuth2Adapter
    client_class = OAuth2Client  

class TwitterLogin(SocialLoginView):
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter
