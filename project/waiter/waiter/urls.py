"""waiter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from customer import views
from django.conf.urls import url
from django.views.generic.base import TemplateView



router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet, 'user')
router.register(r'profile', views.UserProfileViewSet,'userProfile')
router.register(r'menuItems', views.MenuItemViewSet, 'menuItem')
router.register(r'menuCategories', views.MenuCategoryViewSet, 'menuCategories')
router.register(r'orderList', views.OrderListViewSet, 'orderList')
router.register(r'orderRequest', views.OrderRequestViewSet, 'orderRequest')
router.register(r'restaurant', views.RestaurantViewSet, 'restaurant')
router.register(r'openingHours', views.OpeningHoursViewSet, 'openingHours')


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/register/', include('rest_auth.registration.urls')),
    path('rest-auth/facebook/', views.FacebookLogin.as_view(), name='facebook_login'),
    path('rest-auth/google/', views.GoogleLogin.as_view(), name='google_login'),
    path('rest-auth/twitter/', views.TwitterLogin.as_view(), name='twitter_login'),
]
