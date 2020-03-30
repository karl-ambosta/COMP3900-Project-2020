from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import UserSerializer, MenuItemSerializer, MenuCategorySerializer, OrderListSerializer
from .models import MenuItem, MenuCategory, OrderList
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_framework.decorators import action
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import Http404, HttpResponseBadRequest


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_field = 'id'
    lookup_value_regex = '[0-9]+'
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    @action(detail=True)
    def order(self, request, id=None):
        try:
            item = get_object_or_404(self.queryset, id=id)
            owner = get_object_or_404(User.objects.all(), username=self.request.user)
            order_list = get_object_or_404(OrderList.objects.all(), owner=owner)
            order_list.menuItems.add(item)
            return Response(status=status.HTTP_202_ACCEPTED)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True)
    def remove(self, request, id=None):
        try: 
            owner = get_object_or_404(User.objects.all(), username=self.request.user)
            order_list = get_object_or_404(OrderList.objects.all(), owner=owner)
            item = get_object_or_404(self.queryset, id=id)
            order_list.menuItems.remove(item)    
            return Response(status=status.HTTP_202_ACCEPTED)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)


class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request): 
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
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