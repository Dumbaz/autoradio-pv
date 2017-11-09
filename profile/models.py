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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    biography = tinymce_models.HTMLField(_("Biography"), blank=True, null=True)
    website = models.URLField(_("Website"), blank=True)
    googleplus_url = models.URLField(_("Google+ URL"), blank=True)
    facebook_url = models.URLField(_("Facebook URL"), blank=True)
    twitter_url = models.URLField(_("Twitter URL"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True)
    youtube_url = models.URLField(_("Youtube URL"), blank=True)
    dorftv_url = models.URLField(_("DorfTV URL"), blank=True)
    cba_url = models.URLField(_("CBA URL"), blank=True)
    cba_username = models.CharField(_("CBA Username"), blank=True, max_length=60)
    cba_user_token = models.CharField(_("CBA Token"), blank=True, max_length=255)
    ppoi = PPOIField('Image PPOI')
    height = models.PositiveIntegerField('Image Height', blank=True, null=True, editable=False)
    width = models.PositiveIntegerField('Image Width', blank=True, null=True,editable=False)
    image = VersatileImageField(_("Profile picture"), blank=True, null=True, upload_to='user_images', width_field='width', height_field='height', ppoi_field='ppoi')

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        # Generate thumbnails
        if self.image.name and settings.THUMBNAIL_SIZES:
            for size in settings.THUMBNAIL_SIZES:
                thumbnail = self.image.crop[size].name