from django.db import models
from django.contrib.auth.models import User


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
    menuItems = models.ManyToManyField(MenuItem, related_name='ordered_by')


