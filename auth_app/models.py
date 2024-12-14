from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    computing_id = models.CharField(max_length=10, unique=True, blank=True, null=True)
    preferred_name = models.CharField(max_length=255, blank=True, null=True)
    pronoun = models.CharField(max_length=50, blank=True, null=True)
    # profile_photo (add later)

    def __str__(self):
        return self.user.username
    

# signal ensure that whenever a new User is created a corresponding Profile is also created
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()