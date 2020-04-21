from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from .serializers import UserSerializer,UserProfileSerializer, MenuItemSerializer, MenuCategorySerializer, OrderListSerializer, OrderRequestSerializer, RestaurantSerializer, OpeningHoursSerializer, WaiterCallsSerializer
from .models import UserProfile, MenuItem, MenuCategory, OrderList, OrderRequest, Restaurant, OpeningHours, WaiterCalls
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Prefetch

## NOTE: Search for TODO to find what is remaining.
# 1) implement a placing of a new waiter call (Action 1)
# 2) implement the place new order call (Action 3 and 4)

class ChatbotAPILogic:
    def __init__(self):
        # default responses needed for all sub-logic make response changes here
        self.waiter_response = "Not a problem, the waiter has been notified to attend Table "
        self.ingredients_part1 = "I can tell you the following about the "
        self.ingredients_part2 = ": "
        self.order_items = "Not a problem, I have placed an order for "
        self.order_follow_up = ". Is there anything else you would like help with?"
        self.waiter_error = "Sorry, I cannot seem to call the waiter right now, I will notify my developer of this issue!"
        self.ingredients_error_part1 = "Sorry, I cannot seem to find any information on "
        self.ingredients_error_part2 = ". I will let my developer know to get this fixed!"
        self.get = {"MATE":"This is not intended, go away!"}

    def post(self, data: dict) -> dict:
        # extract out the action
        action = data["queryResult"]["action"]

        # extract table number from data dictionary
        try: 
            table_number = int((data)["queryResult"]["outputContexts"][0]["parameters"]["table-number"])
        except KeyError:
            try:
                table_number = int((data)["queryResult"]["outputContexts"][1]["parameters"]["table-number"])
            except:
                    if not (action == "itemfoodinfo.itemfoodinfo-yes"):
                        return Response(status=400)
                    else:
                        pass

        # Action 1: waitercall
        if action == "waitercall.waitercall-yes":
            # place a waiter call in the database here
            called = self.call_waiter(table_number)
            
            # make the response
            if called:
                message = self.waiter_response + str(table_number) + "."
            else:
                message = self.waiter_error
        
        # Action 2: description request
        elif action == "itemfoodinfo.itemfoodinfo-yes":
            # extract food to be ordered here from data dictionary 
            food = data["queryResult"]["outputContexts"][0]["parameters"]["food"]
            
            # fetch description from DB
            description = self.get_food_description(food)

            # make the response
            if not description:
                message = self.ingredients_error_part1 + food + self.ingredients_error_part2
            else:
                message = self.ingredients_part1 + food + self.ingredients_part2 + description

        # Action 3: order a food item (places one only as an order for a table)(new call needs to create new order each i.e. no contexts)
        elif action == "orderfood.orderfood-yes":
            # extract the food item
            food = data["queryResult"]["outputContexts"][1]["parameters"]["food"]
            
            # items to add to customer comments field
            flavour = data["queryResult"]["outputContexts"][1]["parameters"]["flavor"]
            topping = data["queryResult"]["outputContexts"][1]["parameters"]["topping"]
            quantity = int(data["queryResult"]["outputContexts"][1]["parameters"]["amount"])
            
            # build customer comment
            description = flavour + " " + topping
            
            # place order in system here
            ## OPTIONAL: return new order ID and have this come out in chat bot
            order_id = self.place_order(food, quantity, table_number, description)
            
            # make the response
            message = self.order_items + str(quantity) + " "  + food + self.order_follow_up
        
        # Action 4: order a drink item(new call needs to create new order each i.e. no contexts)
        elif action == "order.drink.yes":     
            # extract the drink item
            drink = data["queryResult"]["outputContexts"][1]["parameters"]["drink"]
            
            # items to add to customer comments field
            iced = data["queryResult"]["outputContexts"][1]["parameters"]["iced"]
            milk = data["queryResult"]["outputContexts"][1]["parameters"]["milk-type"]
            quantity = int(data["queryResult"]["outputContexts"][1]["parameters"]["amount"])
            size = data["queryResult"]["outputContexts"][1]["parameters"]["size"]
            
            # build customer comment
            description = iced + " " + size + " " + milk

            # place order in system here
            ## OPTIONAL: return new order ID and have this come out in chat bot
            order_id = self.place_order(drink, quantity, table_number, description)

            # make the response
            message = self.order_items + str(quantity) + " " + drink + self.order_follow_up
        
        # return the dict response
        return ({"fulfillmentText" : message})
    
    # Run a query set filter to pull out description of food
    def get_food_description(self, food:str) -> str:
        qs = MenuItem.objects
        qs = qs.filter(name=food)
        serializer = MenuItemSerializer(qs, many=True)
        try:
            description = serializer.data[0]
            description = description['description']
        except:
            description = ""
        return description

    # TODO
    ## OPTIONAL: return new order ID and have this come out in chat bot
    def place_order(self, item: str, quantity: int, table_number: int , comments: str):
        try:
            owner = get_object_or_404(User.objects.all(), id=3)
            order_list = get_object_or_404(OrderList.objects.filter(status=1,restaurant=1), table_number=table_number)
            menu_item = get_object_or_404(MenuItem.objects.all(), name=item)
            order_list.order_request.create(order_list=order_list, owner=owner, menu_item=menu_item, comments=comments, quantity=quantity)
            order_list.status = 2
            order_list.save()

            return order_list.id
        except Exception as e:
            print(e)
            return -1

    # Need to test
    # Function to call the waiter
    def call_waiter(self, table_num: int) -> bool:
        # call a waiter using the given
        obj, created = WaiterCalls.objects.get_or_create(
            table_number=table_num,
            caller=2,
            status="Customer requires attention",
        )
        if created:
            return True
        else:
            return False