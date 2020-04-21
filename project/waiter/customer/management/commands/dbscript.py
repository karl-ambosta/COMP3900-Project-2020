from django.core.management.base import BaseCommand
from customer.models import *
from django.contrib.auth.models import User

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        

        admin1 = User.objects.create_user('admin1', password='globalpass')
        admin1.is_staff = True
        admin1.save()

        customer1 = User.objects.create_user('customer1', password='globalpass')
        customer2 = User.objects.create_user('customer2', password='globalpass')

        customer1.save()
        customer2.save()

        cashier = User.objects.create_user('cashier', password='globalpass')
        cashier.save()

        kitchen = User.objects.create_user('kitchen', password='globalpass')
        kitchen.save()

        manager = User.objects.create_user('manager', password='globalpass')
        manager.save()

        waiter = User.objects.create_user('waiter', password='globalpass')
        waiter.save()

        admin_profile = UserProfile.objects.get(user=admin1)
        admin_profile.first_name = 'john'
        admin_profile.last_name = 'doe'
        admin_profile.role = 4
        admin_profile.save()

        customer1_profile = UserProfile.objects.get(user=customer1)
        customer2_profile = UserProfile.objects.get(user=customer2)

        customer1_profile.first_name = 'sarah'
        customer1_profile.last_name = 'jane'
        customer1_profile.save()

        customer2_profile.first_name = 'yacob'
        customer2_profile.last_name = 'peralberg'
        customer2_profile.save()
        
        

    