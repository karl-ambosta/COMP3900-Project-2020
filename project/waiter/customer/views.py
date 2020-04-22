from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from .serializers import UserSerializer,UserProfileSerializer, MenuItemSerializer, MenuCategorySerializer, OrderListSerializer, OrderRequestSerializer, RestaurantSerializer, OpeningHoursSerializer, WaiterCallsSerializer, TableSerializer
from .models import UserProfile, MenuItem, MenuCategory, OrderList, OrderRequest, Restaurant, OpeningHours, WaiterCalls, Table
from rest_auth.registration.views import SocialLoginView
from rest_auth.social_serializers import TwitterLoginSerializer
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from rest_auth.social_serializers import TwitterLoginSerializer
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Prefetch, Q
import datetime
from .permissions import MenuItemPermissions, OrderListPermissions, RestaurantAndMenuCategoryPermissions, OpeningHoursPermissions, IsUser, IsCashier, IsCustomer, IsKitchen, IsManager, IsWaiter
from .chatbot import ChatbotAPILogic # Chatbot logic

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUser]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().order_by('order')
    serializer_class = MenuItemSerializer
    lookup_field = 'id'
    lookup_value_regex = '[0-9]+'
    permission_classes = [MenuItemPermissions]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'price', 'menu_category__name']
    
    @action(methods=['post'], detail=True, permission_classes = [IsKitchen | IsManager])
    def move(self, request, id=None):
        obj = self.get_object()
        new_order = request.data.get('order', None)
        if new_order is None:
            return Response(status=status.HTTP_400_BAD_REQUEST,)
        if int(new_order) < 1:
            return Response(status=status.HTTP_400_BAD_REQUEST,)

        MenuItem.objects.move(obj, new_order)
        return Response({'success': True, 'order': new_order})
    
    def create(self, request): # Permissions: Kitchen staff or manager
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    def list(self, request): #Permissions: All Users
        qs = self.get_queryset().filter(active=True)
        qs = self.filter_queryset(qs)
        serializer = MenuItemSerializer(qs, many=True)
        return Response(serializer.data)

    def get_queryset(self): #Permissions: All Users
        qs = MenuItem.objects.order_by('order')
        restaurant = self.request.query_params.get('restaurant', None)
        category = self.request.query_params.get('category', None)
        if restaurant is not None:
            qs = qs.filter(menu_category__restaurant__id=restaurant)
        if category is not None:
            qs = qs.filter(menu_category=category)
        return qs
    
    @action(detail=True, methods=['post'], permission_classes =[IsCustomer|IsKitchen|IsWaiter|IsCashier|IsManager])
    def order(self, request, id=None):
        try:
            item = get_object_or_404(self.queryset, id=id)
            owner = get_object_or_404(User.objects.all(), username=self.request.user)
            order_list = get_object_or_404(OrderList.objects.all(), owner=owner, status=1)
            
            if not item.active:
                return Response('item is no longer available', status=status.HTTP_403_FORBIDDEN)
            if not item.menu_category.restaurant.is_open():
                return Response('restaurant is closed', status=status.HTTP_403_FORBIDDEN)
            if order_list.restaurant.id != item.menu_category.restaurant.id:
                return Response('item belongs to a different restaurant', status=status.HTTP_403_FORBIDDEN)

            order_list.order_request.create(order_list=order_list, owner=owner, menu_item=item, comments=request.data["comments"], quantity=request.data["quantity"])
            return Response(status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes =[IsCustomer|IsWaiter|IsCashier|IsManager|IsKitchen])
    def update_order(self, request, id=None):
        try:
            owner = get_object_or_404(User.objects.all(), username=self.request.user)
            order_list = get_object_or_404(OrderList.objects.filter(status=1), owner=owner)
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
    
    @action(detail=False, permission_classes = [IsKitchen|IsManager|IsWaiter])
    def get_inactive_items(self, request, id=None):
        qs = self.get_queryset().filter(active=False)
        serializer = MenuItemSerializer(qs, many=True)
        return Response(serializer.data)

class MenuCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = MenuCategorySerializer
    permission_classes = [RestaurantAndMenuCategoryPermissions]
    lookup_field = 'id'

    def create(self, request): #Permissions: Manager
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    
    def get_queryset(self): #Permissions: All Users
        qs = MenuCategory.objects.order_by('order')
        restaurant = self.request.query_params.get('restaurant', None)
        if restaurant is not None:
            qs = qs.filter(restaurant__id=restaurant)
        return qs.distinct()

    @action(methods=['post'], detail=True, permission_classes = [IsManager])
    def move(self, request, id=None):
        obj = self.get_object()
        new_order = request.data.get('order', None)
        if new_order is None:
            return Response(status=status.HTTP_400_BAD_REQUEST,)
        if int(new_order) < 1:
            return Response(status=status.HTTP_400_BAD_REQUEST,)

        MenuCategory.objects.move(obj, new_order)
        return Response({'success': True, 'order': new_order})

    def list(self, request):#All Users
        qs = self.get_queryset().prefetch_related(Prefetch('menu_item', queryset=MenuItem.objects.exclude(active=False)))
        serializer = MenuCategorySerializer(qs, many=True)
        return Response(serializer.data)

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

class OrderListViewSet(viewsets.ModelViewSet):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [OrderListPermissions]
    lookup_field = 'id'

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            existing_list = get_object_or_404(OrderList.objects.filter(status=1), owner=request.user)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except:
            try:
                table = get_object_or_404(Table.objects.filter(restaurant=request.data['restaurant']), table_number=request.data['table_number'])
                if table.in_use:
                    return Response('table is in use', status=status.HTTP_403_FORBIDDEN)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                table.in_use = True
                table.save()
                serializer.save(owner=request.user, table_number=table)
                return Response(serializer.data)
            else:
                print(serializer.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'get'], detail=True, permission_classes =[IsCustomer|IsWaiter|IsCashier|IsManager|IsKitchen])
    def send_order(self, request, id=None):
        try:
            order_list = get_object_or_404(OrderList.objects.filter(status=1), id=id)
            order_requests = order_list.order_request.all()
            print(order_requests)
            if order_requests:
                order_list.status = 2
                order_list.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, permission_classes =[IsWaiter|IsManager|IsKitchen])
    def set_order_preparing(self, request, id=None):
        try:
            order_list = get_object_or_404(OrderList.objects.filter(status=2), id=id)
            order_requests = order_list.order_request.all()
            if order_requests:
                order_list.status = 3
                order_list.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, permission_classes =[IsWaiter|IsManager|IsKitchen])
    def set_order_cooking(self, request, id=None):
        try:
            order_list = get_object_or_404(OrderList.objects.filter(status=3), id=id)
            order_requests = order_list.order_request.all()
            if order_requests:
                order_list.status = 4
                order_list.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, permission_classes =[IsWaiter|IsManager|IsKitchen|IsCashier])
    def set_order_pickup(self, request, id=None):
        try:
            order_list = get_object_or_404(OrderList.objects.filter(status=4), id=id)
            order_requests = order_list.order_request.all()
            if order_requests:
                order_list.status = 5
                order_list.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['post'], detail=True, permission_classes =[IsWaiter|IsManager|IsKitchen|IsCashier])
    def set_order_served(self, request, id=None):
        try:
            order_list = get_object_or_404(OrderList.objects.filter(status=5), id=id)
            order_requests = order_list.order_request.all()
            if order_requests:
                order_list.status = 6
                order_list.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, permission_classes =[IsCustomer|IsWaiter|IsManager|IsKitchen|IsCashier])
    def set_order_waiting_payment(self, request, id=None):
        try:
            order_list = get_object_or_404(OrderList.objects.filter(status=6), id=id)
            order_requests = order_list.order_request.all()
            if order_requests:
                order_list.status = 7
                order_list.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, permission_classes =[IsWaiter|IsManager|IsCashier])
    def set_order_paid(self, request, id=None):
        try:
            order_list = get_object_or_404(OrderList.objects.filter(status=7), id=id)
            table = get_object_or_404(Table.objects.filter(restaurant=order_list.restaurant), table_number=order_list.table_number.table_number)
            order_requests = order_list.order_request.all()
            if order_requests:
                order_list.status = 8
                table.in_use = False
                table.save()
                order_list.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def get_kitchen_orders(self, request, id=None, permission_classes =[IsCustomer|IsWaiter|IsCashier|IsManager|IsKitchen]):
        qs = self.get_queryset().filter(Q(status=2) | Q(status=3) | Q(status=4) | Q(status=5))
        serializer = OrderListSerializer(qs, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def get_order_history(self, request, id=None, permission_classes =[IsCustomer|IsWaiter|IsCashier|IsManager|IsKitchen]):
        qs = self.get_queryset().filter(Q(status=6) | Q(status=7) | Q(status=8))
        serializer = OrderListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def get_waiter_orders(self, request, id=None, permission_classes = [permissions.IsAuthenticated]):
        qs = self.get_queryset().filter(Q(status=5) | Q(status=6))
        serializer = OrderListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, permission_classes = [permissions.IsAuthenticated])
    def get_cashier_orders(self, request, id=None):
        qs = self.get_queryset().filter(Q(status=7)) # removed:  | Q(status=8)
        serializer = OrderListSerializer(qs, many=True)
        return Response(serializer.data)    

    def get_queryset(self):
        qs = OrderList.objects.order_by('id')
        restaurant = self.request.query_params.get('restaurant', None)
        user = self.request.query_params.get('user', None)
        if restaurant is not None:
            qs = qs.filter(restaurant__id=restaurant)
        if user is not None:
            qs = qs.filter(owner_id=user)
        return qs   

class OrderRequestViewSet(viewsets.ModelViewSet):
    queryset = OrderRequest.objects.all().order_by('id')
    serializer_class = OrderRequestSerializer
    permission_classes = [IsCustomer| IsWaiter|IsKitchen |IsCashier|IsManager]
    
    def create(self, request): 
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        qs = OrderRequest.objects.order_by('id')
        orderList = self.request.query_params.get('order_list', None)
        if orderList is not None:
            qs = qs.filter(order_list__id=orderList)
        return qs

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]
    #permission_classes = [RestaurantAndMenuCategoryPermissions]
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'order_list']
    lookup_field = 'id'

    def create(self, request): 
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsManager|IsWaiter|IsCashier])
    def create_tables(self, request, id=None):
        try:
            restaurant = get_object_or_404(Restaurant.objects.all(), id=id)
            for i in range(1, restaurant.total_tables + 1):
                Table.objects.get_or_create(table_number=i, restaurant=restaurant)
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def get_all_earnings(self, request, id=None):
        try:
            restaurant = get_object_or_404(Restaurant.objects.all(), id=id)
            earnings = OrderList.objects.filter(restaurant=restaurant, status=8).aggregate(Sum('order_total'))
            return Response({'earnings': earnings['order_total__sum']}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def get_monthly_earnings(self, request, id=None):
        try:
            restaurant = get_object_or_404(Restaurant.objects.all(), id=id)
            all_earnings = {}
            for year in OrderList.objects.filter(restaurant=restaurant, status=8).datetimes('created_at', 'year'):
                all_earnings[year.year] = {}
                for i in range(1,13):
                    earnings = OrderList.objects.filter(restaurant=restaurant, status=8, created_at__month=i, created_at__year=year.year).aggregate(Sum('order_total'))        
                    all_earnings[year.year][i] = earnings['order_total__sum']
            return Response(all_earnings, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True)
    def get_yearly_earnings(self, request, id=None):
        try:
            restaurant = get_object_or_404(Restaurant.objects.all(), id=id)
            all_earnings = {}
            for year in OrderList.objects.filter(restaurant=restaurant, status=8).datetimes('created_at', 'year'):
                earnings = OrderList.objects.filter(restaurant=restaurant, status=8, created_at__year=year.year).aggregate(Sum('order_total'))
                all_earnings[year.year] = earnings['order_total__sum']
            return Response(all_earnings, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True)
    def get_available_tables(self, request, id=None):
        try:
            restaurant = get_object_or_404(Restaurant.objects.all(), id=id)
            number_of_tables = Table.objects.filter(restaurant=restaurant, in_use=False).count()
            return Response({'tables_free': number_of_tables}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def get_table_turnover(self, request, id=None):
        try:
            restaurant = get_object_or_404(Restaurant.objects.all(), id=id)
            hours = restaurant.opening_hours.get(day=datetime.today().weekday()+1)
            if hours:
                if hours.to_hour == time(0,0,0):
                    tomorrow = datetime.today() + timedelta(days=1)
                    to_h = datetime.combine(tomorrow, hours.to_hour)
                else:
                    to_h = datetime.combine(datetime.today(), hours.to_hour)
                from_h = datetime.combine(datetime.today(), hours.from_hour)
                diff = to_h - from_h
                hours_open = diff.total_seconds() / 3600
            turnover = OrderList.objects.filter(restaurant=restaurant, created_at__date=datetime.now().date()).count() / hours_open
            return Response({'turnover': '{0:.2f}'.format(turnover)}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def get_average_dishes_per_order(self, request, id=None):
        try:
            restaurant = get_object_or_404(Restaurant.objects.all(), id=id)
            avg = OrderList.objects.filter(restaurant=restaurant, status__range=(2,8)).aggregate(Avg('order_request__quantity'))['order_request__quantity__avg']
            return Response({'average': '{0:.2f}'.format(avg)}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OpeningHoursViewSet(viewsets.ModelViewSet):
    queryset = OpeningHours.objects.all()
    serializer_class = OpeningHoursSerializer
    permission_classes = [OpeningHoursPermissions]

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

class WaiterCallsViewSet(viewsets.ModelViewSet):
    # use cases needed:
    #   1) list all for waiter view (view) - done
    #   2) kitchen hits ready for pickup and creates an entry (create) - need to implement in backend
    #   3) customer calls waiter and creates an entry (create) - frontend does this bit
    #   4) waiter hits completed and this deletes the entry (delete) - frontend can do this

    queryset = WaiterCalls.objects.all()
    serializer_class = WaiterCallsSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def create(self, request):
        return Response(status=status.HTTP_403_FORBIDDEN)