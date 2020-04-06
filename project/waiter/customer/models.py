from django.db import models
from django.contrib.auth.models import User
import uuid

def generate_profile_id():
    return str(uuid.uuid4()).split("-")[-1] #generate unique user id

class UserProfile(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_id = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} - {}".format(self.title, self.profile_id)

    def save(self, *args, **kwargs):
        if len(self.profile_id.strip(" "))==0:
            self.profile_id = generate_profile_id()

        super(UserProfile, self).save(*args, **kwargs) # Call the real   save() method

class MenuCategory(models.Model):
    """ 
    Menu categories
    """
    name = models.CharField(max_length=50)

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
    owner = models.ForeignKey(User, related_name='order_list', on_delete=models.CASCADE)

class OrderRequest(models.Model):
    """
    details of an individual order
    """

    order_list = models.ForeignKey(OrderList, related_name='order_request', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name='order_request', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, related_name='order_request', on_delete=models.CASCADE)
    comments = models.CharField(max_length=300)
    quantity = models.PositiveIntegerField()