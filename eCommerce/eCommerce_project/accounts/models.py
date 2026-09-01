from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    """ 
    Extends User model
    Stores whether user is a Vendor or Buyer
    """
    USER_TYPES = (
        ('vendor', 'Vendor'),
        ('buyer', 'Buyer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='buyer')

    def __str__(self):
        """ String representation of profile """
        return f"{self.user.username} ({self.get_user_type_display()})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ 
    Creating a new profile when a new User is created
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ 
    Saving the related profile whenever a User is saved
    """
    instance.profile.save()