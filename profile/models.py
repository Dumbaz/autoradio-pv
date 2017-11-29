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
    biography = tinymce_models.HTMLField(_("Biography"), blank=True, null=True, help_text=_("Describe yourself and your fields of interest in a few sentences."))
    website = models.URLField(_("Website"), blank=True, help_text=_("URL to your personal website."))
    googleplus_url = models.URLField(_("Google+ URL"), blank=True, help_text=_("URL to your Google+ profile."))
    facebook_url = models.URLField(_("Facebook URL"), blank=True, help_text=_("URL to your Facebook profile."))
    twitter_url = models.URLField(_("Twitter URL"), blank=True, help_text=_("URL to your Twitter profile."))
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True, help_text=_("URL to your LinkedIn profile."))
    youtube_url = models.URLField(_("Youtube URL"), blank=True, help_text=_("URL to your Youtube channel."))
    dorftv_url = models.URLField(_("DorfTV URL"), blank=True, help_text=_("URL to your dorfTV channel."))
    cba_url = models.URLField(_("CBA URL"), blank=True, help_text=_("URL to your CBA profile."))
    cba_username = models.CharField(_("CBA Username"), blank=True, max_length=60, help_text=_("Your username in CBA. This is necessary for uploading files to your account."))
    cba_user_token = models.CharField(_("CBA Token"), blank=True, max_length=255, help_text=_("The CBA upload token for your account. This is NOT your password which you use to log into CBA!"))
    ppoi = PPOIField('Image PPOI')
    height = models.PositiveIntegerField('Image Height', blank=True, null=True, editable=False)
    width = models.PositiveIntegerField('Image Width', blank=True, null=True,editable=False)
    image = VersatileImageField(_("Profile picture"), blank=True, null=True, upload_to='user_images', width_field='width', height_field='height', ppoi_field='ppoi', help_text=_("Upload a picture of yourself. Images are automatically cropped around the 'Primary Point of Interest'. Click in the image to change it and press Save."))

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