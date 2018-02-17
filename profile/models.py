from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from versatileimagefield.fields import VersatileImageField, PPOIField
from django.conf import settings
import os

from tinymce import models as tinymce_models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', editable=False)
    cba_username = models.CharField(_("CBA Username"), blank=True, max_length=60, help_text=_("Your username in CBA. This is necessary for uploading files to your account."))
    cba_user_token = models.CharField(_("CBA Token"), blank=True, max_length=255, help_text=_("The CBA upload token for your account. This is NOT your password which you use to log into CBA!"))

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)