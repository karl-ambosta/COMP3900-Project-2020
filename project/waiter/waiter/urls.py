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
router.register(r'waiterCalls', views.WaiterCallsViewSet, 'waiterCalls')
router.register(r'tables', views.TableViewSet, 'tables')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/register/', include('rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),
    path('rest-auth/facebook/', views.FacebookLogin.as_view(), name='facebook_login'),
    path('rest-auth/google/', views.GoogleLogin.as_view(), name='google_login'),
    path('rest-auth/twitter/', views.TwitterLogin.as_view(), name='twitter_login'),
    path(r'chatBot/', views.chatBotViewSet.as_view())
]
