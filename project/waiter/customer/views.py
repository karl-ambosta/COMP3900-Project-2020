from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from .serializers import UserSerializer,UserProfileSerializer, MenuItemSerializer, MenuCategorySerializer, OrderListSerializer, OrderRequestSerializer, RestaurantSerializer, OpeningHoursSerializer
from .models import UserProfile, MenuItem, MenuCategory, OrderList, OrderRequest, Restaurant, OpeningHours
from rest_auth.registration.views import SocialLoginView
from rest_auth.social_serializers import TwitterLoginSerializer
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Prefetch

# Chatbot logic
from .chatbot import ChatbotAPILogic

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().order_by('order')
    serializer_class = MenuItemSerializer
    lookup_field = 'id'
    lookup_value_regex = '[0-9]+'
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'price', 'menu_category__name']
    
    @action(methods=['post'], detail=True)
    def move(self, request, id=None):
        obj = self.get_object()
        new_order = request.data.get('order', None)
        if new_order is None:
            return Response(status=status.HTTP_400_BAD_REQUEST,)
        if int(new_order) < 1:
            return Response(status=status.HTTP_400_BAD_REQUEST,)

        MenuItem.objects.move(obj, new_order)
        return Response({'success': True, 'order': new_order})
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    def list(self, request):
        qs = self.get_queryset().filter(active=True)
        qs = self.filter_queryset(qs)
        serializer = MenuItemSerializer(qs, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        qs = MenuItem.objects.order_by('order')
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
    
    @action(detail=False)
    def get_inactive_items(self, request, id=None):
        qs = self.get_queryset().filter(active=False)
        serializer = MenuItemSerializer(qs, many=True)
        return Response(serializer.data)

class MenuCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def create(self, request): 
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    
    def get_queryset(self):
        qs = MenuCategory.objects.order_by('order')
        restaurant = self.request.query_params.get('restaurant', None)
        if restaurant is not None:
            qs = qs.filter(restaurant__id=restaurant)
        return qs.distinct()

    @action(methods=['post'], detail=True)
    def move(self, request, id=None):
        obj = self.get_object()
        new_order = request.data.get('order', None)
        if new_order is None:
            return Response(status=status.HTTP_400_BAD_REQUEST,)
        if int(new_order) < 1:
            return Response(status=status.HTTP_400_BAD_REQUEST,)

        MenuCategory.objects.move(obj, new_order)
        return Response({'success': True, 'order': new_order})

    def list(self, request):
        qs = self.get_queryset().filter(menu_item__active=True).prefetch_related(Prefetch('menu_item', queryset=MenuItem.objects.filter(active=True)))
        serializer = MenuCategorySerializer(qs, many=True)
        return Response(serializer.data)

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
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request): 
        return Response(status=status.HTTP_204_NO_CONTENT)  

class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    basic_auth = False

class GoogleLogin(SocialLoginView):
    adapter_class = CustomGoogleOAuth2Adapter
    client_class = OAuth2Client  

class TwitterLogin(SocialLoginView):
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter

class chatBotViewSet(APIView):
    chatbot = ChatbotAPILogic()

    # test function to get onto rest framework, ignore
    def get(self, request):
        return Response(self.chatbot.get)
    
    # post's are sent to one address by dialogflow, this is all that's needed
    def post(self, request):
        # if empty json else
        if not bool(request.data):
            return Response(status=400)
        else:
            return Response(self.chatbot.post(request.data))