from django.core.management.base import BaseCommand
from customer.models import *
from django.contrib.auth.models import User

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        

        admin1 = User.objects.create_user('admin1', password='globalpass')
        admin1.save()

        customer1 = User.objects.create_user('customer1', password='globalpass')
        customer2 = User.objects.create_user('customer2', password='globalpass')
        customer3 = User.objects.create_user('customer3', password='globalpass')
        customer4 = User.objects.create_user('customer4', password='globalpass')
        customer5 = User.objects.create_user('customer5', password='globalpass')

        customer1.save()
        customer2.save()
        customer3.save()
        customer4.save()
        customer5.save()

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
        admin_profile.role
        

    