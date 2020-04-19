from django.db import models, transaction
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.db.models import Sum, F, ExpressionWrapper, Max, When, Q
from datetime import *

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

    def is_open(self):
        opening = self.opening_hours.get(day=datetime.today().weekday()+1)
        return opening.from_hour <= datetime.time(datetime.now()) < opening.to_hour


class MenuCategoryOrderManager(models.Manager):
    def move(self, object, new_order):
        qs = self.get_queryset()

        with transaction.atomic():
            if object.order > int(new_order):
                qs.filter(restaurant=object.restaurant, order__lt=object.order, order__gte=new_order,).exclude(id=object.id).update(order=F('order') + 1,)
            else:
                qs.filter(restaurant=object.restaurant, order__lte=new_order, order__gt=object.order,).exclude(id=object.id,).update(order=F('order') - 1,)
            object.order = new_order
            object.save()
    
    def create(self, **kwargs):
        instance = self.model(**kwargs)

        with transaction.atomic():
            results = self.filter(restaurant=instance.restaurant).aggregate(Max('order'))
            
            current_order = results['order__max']
            if current_order is None:
                current_order = 0

            value = current_order + 1
            instance.order = value
            instance.save()

            return instance


class MenuCategory(models.Model):
    """ 
    Menu categories
    """
    name = models.CharField(max_length=50)
    restaurant = models.ForeignKey(Restaurant, related_name='menu_categories', on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    objects = MenuCategoryOrderManager()


class MenuItemOrderManager(models.Manager):
    def move(self, object, new_order):
        qs = self.get_queryset()

        with transaction.atomic():
            if object.order > int(new_order):
                qs.filter(menu_category=object.menu_category, order__lt=object.order, order__gte=new_order,).exclude(id=object.id).update(order=F('order') + 1,)
            else:
                qs.filter(menu_category=object.menu_category, order__lte=new_order, order__gt=object.order,).exclude(id=object.id,).update(order=F('order') - 1,)
            object.order = new_order
            object.save()
    
    def create(self, **kwargs):
        instance = self.model(**kwargs)

        with transaction.atomic():
            results = self.filter(menu_category=instance.menu_category).aggregate(Max('order'))
            
            current_order = results['order__max']
            if current_order is None:
                current_order = 0

            value = current_order + 1
            instance.order = value
            instance.save()

            return instance


class MenuItem(models.Model):
    """
    Menu items    
    """ 
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.CharField(max_length=300)
    menu_category = models.ForeignKey(MenuCategory, related_name='menu_item', on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='media/menu/', default='/media/menu/defaultmenuitem.png')
    order = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    objects = MenuItemOrderManager()


class OrderListAnnotatedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            order_total = ExpressionWrapper(
                Sum(
                    F('order_request__quantity') * F('order_request__menu_item__price')
                ),
                output_field=models.DecimalField(decimal_places=2, max_digits=9)
            )
        )

class OrderList(models.Model):
    """
    The current active order list of the user
    """
    ORDER_STATUS = [
        (1, 'Active'),
        (2, 'Received'),
        (3, 'Preparing'),
        (4, 'Cooking'),
        (5, 'Pickup ready'),
        (6, 'Served'),
        (7, 'Paid')
    ]

    owner = models.ForeignKey(User, related_name='order_lists', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='order_lists', on_delete=models.CASCADE)
    table_number = models.IntegerField()
    status = models.PositiveSmallIntegerField(choices=ORDER_STATUS)
    objects = OrderListAnnotatedManager()


class OrderRequestAnnotatedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            total=ExpressionWrapper(
                F('quantity') * F('menu_item__price'),
                output_field = models.DecimalField(decimal_places=2, max_digits=9)
            )
        )

class OrderRequest(models.Model):
    """
    details of an individual order
    """

    order_list = models.ForeignKey(OrderList, related_name='order_request', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name='order_request', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, related_name='order_request', on_delete=models.CASCADE)
    comments = models.CharField(max_length=300)
    quantity = models.PositiveIntegerField()
    objects = OrderRequestAnnotatedManager()


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

class WaiterCalls(models.Model):
    """
    Model to track active waiter calls
    """

    CALLER_NAME = [
        (1, 'Kitchen'),
        (2, 'Customer'),
    ]

    created = models.TimeField(auto_now_add=True)
    table_number = models.PositiveSmallIntegerField()
    caller = models.PositiveSmallIntegerField(choices=CALLER_NAME)
    status = models.CharField(max_length=30)

    class Meta:
        ordering = ['created']