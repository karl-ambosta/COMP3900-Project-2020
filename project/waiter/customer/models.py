from django.db import models
from django.contrib.auth.models import User
import uuid 
from django.db.models.signals import post_save

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True)
    #genre = models.CharField(max_length=1, choices=GENRE_CHOICES, null=True)
    address = models.CharField(max_length=150, null=True)
    postal_code_4 = models.PositiveIntegerField(null=True)
    postal_code_3 = models.PositiveIntegerField(null=True)
    #locatity = models.CharField(max_length=30, null=True)
    #marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES, null=True)
    #child_amount = models.PositiveSmallIntegerField(null=True)
    #is_merchant = models.BooleanField(default=False)
    #store = models.ForeignKey(Store, null=True)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)






'''
def generate_profile_id():
   return str(uuid.uuid4()).split("-")[-1] #generate unique user id

class UserProfile(models.Model):
    name = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #user = models.ForeignKey(User,related_name="usernames", on_delete=models.CASCADE)
    #email = models.ForeignKey(User, related_name='userprofile', on_delete=models.CASCADE, null=True)
    #email = models.ForeignKey(User,on_delete=models.CASCADE,related_name="emails", blank=True)
    profile_id = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} - {}".format(self.title, self.profile_id)

    def save(self, *args, **kwargs):
        if len(self.profile_id.strip(" "))==0:
            self.profile_id = generate_profile_id()

        super(UserProfile, self).save(*args, **kwargs) # Call the real   save() method
'''
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