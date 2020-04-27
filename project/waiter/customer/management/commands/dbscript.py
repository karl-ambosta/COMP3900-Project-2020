from django.core.management.base import BaseCommand
from customer.models import *
from django.contrib.auth.models import User
import datetime
import random
import requests

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        
        """
        Create Users
        """
        admin1 = User.objects.create_user('admin1', email='admin1@user.com', password='globalpass')
        admin1.is_staff = True
        admin1.save()

        cashier = User.objects.create_user('cashier', email='cashier@user.com', password='globalpass')
        cashier.save()

        kitchen = User.objects.create_user('kitchen', email='kitchen@user.com',password='globalpass')
        kitchen.save()

        manager = User.objects.create_user('manager', email='manager@user.com', password='globalpass')
        manager.save()

        waiter = User.objects.create_user('waiter', email='waiter@user.com', password='globalpass')
        waiter.save()

        customer1 = User.objects.create_user('customer1', email='customer1@user.com', password='globalpass')
        customer2 = User.objects.create_user('customer2', email='customer2@user.com', password='globalpass')
        customer1.save()
        customer2.save()

        """
        Edit Profiles
        """
        admin_profile = UserProfile.objects.get(user=admin1)
        admin_profile.first_name = 'John'
        admin_profile.last_name = 'Doe'
        admin_profile.role = 4 #Manager
        admin_profile.save()

        cashier_profile = UserProfile.objects.get(user=cashier)
        cashier_profile.first_name = 'Bob'
        cashier_profile.last_name = 'Jones'
        cashier_profile.role = 2 #Cashier
        cashier_profile.save()

        kitchen_profile = UserProfile.objects.get(user=kitchen)
        kitchen_profile.first_name = 'Charlie'
        kitchen_profile.last_name = 'Pel'
        kitchen_profile.role = 3 #Kitchen
        kitchen_profile.save()

        manager_profile = UserProfile.objects.get(user=manager)
        manager_profile.first_name = 'George'
        manager_profile.last_name = 'Bone'
        manager_profile.role = 4 #Manager
        manager_profile.save()

        waiter_profile = UserProfile.objects.get(user=waiter)
        waiter_profile.first_name = 'Timmy'
        waiter_profile.last_name = 'Trumpet'
        waiter_profile.role = 5 #Waiter
        waiter_profile.save()

        customer1_profile = UserProfile.objects.get(user=customer1)
        customer1_profile.first_name = 'Sarah'
        customer1_profile.last_name = 'Jane'
        customer1_profile.save()

        customer2_profile = UserProfile.objects.get(user=customer2)
        customer2_profile.first_name = 'Yacob'
        customer2_profile.last_name = 'Peralberg'
        customer2_profile.save()

        """
        Create Restaurants

        """

        restaurant1 = Restaurant.objects.create(name='UNSW Cafe', description='Cafe Located in K17 at UNSW', total_tables=20)
        restaurant1.save()

        restaurant2 = Restaurant.objects.create(name = 'Anzac Parade Cafe', description = 'Cafe Located on Anzac Parade', total_tables = 20)
        restaurant2.save()

        restaurant3 = Restaurant.objects.create(name = 'Barker St Cafe', description = 'Cafe Located on Barker Street', total_tables = 20)
        restaurant3.save()


        """
        Opening Hours and Categories
        """
        restaurant1 = Restaurant.objects.get(name='UNSW Cafe')
        restaurant2 = Restaurant.objects.get(name='Anzac Parade Cafe')
        restaurant3 = Restaurant.objects.get(name = 'Barker St Cafe')

        for i in range(1,8): 
            restaurant1_hours = OpeningHours.objects.create(restaurant = restaurant1, day = i, from_hour = datetime.time(6, 00),to_hour = datetime.time(23, 00))
            restaurant2_hours = OpeningHours.objects.create(restaurant = restaurant2, day = i, from_hour = datetime.time(6, 00),to_hour = datetime.time(23, 00))
            restaurant3_hours = OpeningHours.objects.create(restaurant = restaurant3, day = i, from_hour = datetime.time(6, 00),to_hour = datetime.time(23, 00))
            restaurant1_hours.save()
            restaurant2_hours.save()
            restaurant3_hours.save()

        categories = ['Entree', 'Breakfast', 'Lunch', 'Dinner', 'Specials', 'Drinks']
        for i,cat in enumerate(categories): 
            restaurant1_cat = MenuCategory.objects.create(name=cat,restaurant = restaurant1, order=i)
            restaurant2_cat = MenuCategory.objects.create(name=cat,restaurant = restaurant2, order=i)
            restaurant3_cat = MenuCategory.objects.create(name=cat,restaurant = restaurant3, order=i)
            restaurant1_cat.save()
            restaurant2_cat.save()
            restaurant3_cat.save()

        """
        Add Menu Items

        """ 
        
        foods =  { 
                "Entree": ['Pumpkin Soup', 'Sourdough Bread', 'Chicken Soup', 'Spring Rolls', 'Garlic Bread', 'Cheese Toast'], 
                "Breakfast": ['Bacon & Egg Roll', 'Scrambled Eggs', 'French Toast', 'Big Brekkie', 'Eggs Benedict', 'Salmon Roll'],
                "Lunch": ['Grilled Salmon', 'Big Burger', 'Steak Sandwich', 'Salad', 'Gourmet Pizza', 'Cheese Pizza'],
                "Dinner": ['Classic Roast', 'Spaghetti Bolognese', 'Fish & Chips', 'Steak & Chips', 'Roast Chicken & Salad', 'Butter Chicken with Rice'],
                "Specials": ['Seafood Sensation', 'Fried Rice', 'Grilled Fish & Chips', 'Vegetarian Pizza', 'Steamed Veggies', 'Dumplings'],
                "Drinks": ['Coca Cola', 'Latte', 'Red Wine', 'Sparkling Water', 'Coffee', 'Lemon & Lime Bitters']
            }


        count = 1
        for i,cat in enumerate(categories):

            cat_object = MenuCategory.objects.get(id=(count))
            restaurant1_menuitems1 = MenuItem.objects.create(name = foods[cat][0], price = round(random.randrange(10,20),2),description = foods[cat][0], order = i+1, menu_category=cat_object)
            restaurant1_menuitems1.save()
            
            restaurant1_menuitems2 = MenuItem.objects.create(name=foods[cat][1], price = round(random.randrange(10,20),2),description = foods[cat][1], order = i+2, menu_category=cat_object)
            restaurant1_menuitems2.save()
            
            count = count + 1
            cat_object = MenuCategory.objects.get(id=(count))                   
            restaurant2_menuitems1 = MenuItem.objects.create(name=foods[cat][2],price= round(random.randrange(10,20),2),description = foods[cat][2], order = i+1, menu_category=cat_object)
            restaurant2_menuitems1.save()
            restaurant2_menuitems2 = MenuItem.objects.create(name=foods[cat][3],price= round(random.randrange(10,20),2),description = foods[cat][3], order = i+2, menu_category=cat_object)
            restaurant2_menuitems2.save()
            
            count = count + 1    
            cat_object = MenuCategory.objects.get(id=(count))   
            restaurant3_menuitems1 = MenuItem.objects.create(name=foods[cat][4],price= round(random.randrange(10,20),2),description = foods[cat][4],  order = i+1, menu_category=cat_object)
            restaurant3_menuitems1.save()
            restaurant3_menuitems2 = MenuItem.objects.create(name=foods[cat][5],price= round(random.randrange(10,20),2),description = foods[cat][5], order = i+2, menu_category=cat_object)
            restaurant3_menuitems2.save()
            
            count = count + 1  
        
            
            
            
                