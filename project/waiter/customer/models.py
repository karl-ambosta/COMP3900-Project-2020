from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
#import uuid 
from django.db.models.signals import post_save, pre_delete

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name='profile',on_delete=models.CASCADE )
    #uid = models.CharField(max_length=20, null=False, blank=False)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def create_profile_for_user(sender, instance=None, created=False, **kargs):
        if created:
            UserProfile.objects.get_or_create(user=instance)

    @receiver(pre_delete, sender=User)
    def delete_profile_for_user(sender, instance=None, **kargs):
        if instance:
            user_profile = UserProfile.objects.get(user=instance)
            user_profile.delete()

class Restaurant(models.Model):
    """ 
    Restaurant model - stores the information of the specific restaurant and is used to determine which one the user is ordering from
    """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)


class MenuCategory(models.Model):
    """ 
    Menu categories
    """
    name = models.CharField(max_length=50)
    restaurant = models.ForeignKey(Restaurant, related_name='menu_categories', on_delete=models.CASCADE)


class MenuItem(models.Model):
    """
    Menu items    
    """ 
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.CharField(max_length=300)
    menu_category = models.ForeignKey(MenuCategory, related_name='menu_item', on_delete=models.CASCADE)


class OrderList(models.Model):
    """
    The current active order list of the user
    """
    owner = models.OneToOneField(User, related_name='order_list', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='order_lists', on_delete=models.CASCADE)


class OrderRequest(models.Model):
    """
    details of an individual order
    """

    order_list = models.ForeignKey(OrderList, related_name='order_request', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name='order_request', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, related_name='order_request', on_delete=models.CASCADE)
    comments = models.CharField(max_length=300)
    quantity = models.PositiveIntegerField()


class OpeningHours(models.Model):
    """
    model to store each individual opening hour time slot per restaurant
    """

    WEEKDAYS = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    ]

    restaurant = models.ForeignKey(Restaurant, related_name='opening_hours', on_delete=models.CASCADE)
    day = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    from_hour = models.TimeField()
    to_hour = models.TimeField()
