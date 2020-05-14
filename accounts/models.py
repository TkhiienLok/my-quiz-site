from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse


GENDER_CHOICES = (
   ('M', 'Male'),
   ('F', 'Female')
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(default='', blank=True)
    email_confirmed = models.BooleanField(default=False)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=30, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('accounts:guest-view-profile', kwargs={
            'pk': self.user.pk,
        })

    def __str__(self):
        return '{0}, {1}'.format(self.user.last_name, self.user.first_name)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()
