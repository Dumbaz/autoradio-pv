# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-29 18:28
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='biography',
            field=tinymce.models.HTMLField(blank=True, help_text='Describe yourself and your fields of interest in a few sentences.', null=True, verbose_name='Biography'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cba_url',
            field=models.URLField(blank=True, help_text='URL to your CBA profile.', verbose_name='CBA URL'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cba_user_token',
            field=models.CharField(blank=True, help_text='The CBA upload token for your account. This is NOT your password which you use to log into CBA!', max_length=255, verbose_name='CBA Token'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cba_username',
            field=models.CharField(blank=True, help_text='Your username in CBA. This is necessary for uploading files to your account.', max_length=60, verbose_name='CBA Username'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='dorftv_url',
            field=models.URLField(blank=True, help_text='URL to your dorfTV channel.', verbose_name='DorfTV URL'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='facebook_url',
            field=models.URLField(blank=True, help_text='URL to your Facebook profile.', verbose_name='Facebook URL'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='googleplus_url',
            field=models.URLField(blank=True, help_text='URL to your Google+ profile.', verbose_name='Google+ URL'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(blank=True, height_field='height', help_text="Upload a picture of yourself. Images are automatically cropped around the 'Primary Point of Interest'. Click in the image to change it and press Save.", null=True, upload_to='user_images', verbose_name='Profile picture', width_field='width'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='linkedin_url',
            field=models.URLField(blank=True, help_text='URL to your LinkedIn profile.', verbose_name='LinkedIn URL'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='twitter_url',
            field=models.URLField(blank=True, help_text='URL to your Twitter profile.', verbose_name='Twitter URL'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='website',
            field=models.URLField(blank=True, help_text='URL to your personal website.', verbose_name='Website'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='youtube_url',
            field=models.URLField(blank=True, help_text='URL to your Youtube channel.', verbose_name='Youtube URL'),
        ),
    ]
