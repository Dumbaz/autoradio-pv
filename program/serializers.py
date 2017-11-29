from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.response import Response
from program.models import Show, TimeSlot, Category, Host, Language, Topic, MusicFocus, Note
from profile.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    # Add profile fields to JSON
    profile = ProfileSerializer()

    class Meta:
        model = User
        exclude = ('password',)
        #fields = '__all__'


    def update(self, instance, validated_data):
        """
        Update and return an existing User instance, given the validated data.
        """

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)

        profile = Profile.objects.get(user=instance.id)
        profile.biography = validated_data['profile'].get('biography')
        profile.website = validated_data['profile'].get('website')
        profile.googleplus_url = validated_data['profile'].get('googleplus_url')
        profile.facebook_url = validated_data['profile'].get('facebook_url')
        profile.twitter_url = validated_data['profile'].get('twitter_url')
        profile.linkedin_url = validated_data['profile'].get('linkedin_url')
        profile.youtube_url = validated_data['profile'].get('youtube_url')
        profile.dorftv_url = validated_data['profile'].get('dorftv_url')
        profile.cba_url = validated_data['profile'].get('cba_url')
        profile.cba_username = validated_data['profile'].get('cba_username')
        profile.cba_user_token = validated_data['profile'].get('cba_user_token')
        profile.save()

        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class MusicFocusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicFocus
        fields = '__all__'


class ShowSerializer(serializers.HyperlinkedModelSerializer):
    category = CategorySerializer(many=True)
    hosts = HostSerializer(many=True)
    language = LanguageSerializer(many=True)
    topic = TopicSerializer(many=True)
    musicfocus = MusicFocusSerializer(many=True)

    class Meta:
        model = Show
        fields = ('id', 'name', 'slug', 'image', 'logo', 'short_description', 'description',
                  'email', 'website', 'created', 'last_updated', 'type_id', 'rtrcategory_id',
                  'predecessor_id', 'cba_series_id', 'fallback_pool', 'category', 'hosts',
                  'language', 'topic', 'musicfocus')


    def create(self, validated_data):
        """
        Create and return a new Show instance, given the validated data.
        """
        return Show.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        Update and return an existing Show instance, given the validated data.
        """

        instance.name = validated_data.get('name', instance.name)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.image = validated_data.get('image', instance.image)
        instance.logo = validated_data.get('logo', instance.logo)
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.description = validated_data.get('description', instance.description)
        instance.email = validated_data.get('email', instance.email)
        instance.website = validated_data.get('website', instance.website)
        instance.cba_series_id = validated_data.get('cba_series_id', instance.cba_series_id)
        instance.fallback_pool = validated_data.get('fallback_pool', instance.fallback_pool)
        instance.save()
        return instance


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'


    def create(self, validated_data):
        """
        Create and return a new TimeSlot instance, given the validated data.
        """
        return TimeSlot.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        Update and return an existing Show instance, given the validated data.
        """

        instance.memo = validated_data.get('memo', instance.memo)
        instance.is_repetition = validated_data.get('is_repetition', instance.is_repetition)
        instance.playlist_id = validated_data.get('playlist_id', instance.playlist_id)
        instance.save()
        return instance


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'


    def create(self, validated_data):
        """
        Create and return a new Note instance, given the validated data.
        """

        return Note.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        Update and return an existing Note instance, given the validated data.
        """

        instance.show_id = validated_data.get('show_id', instance.show_id)
        instance.timeslot_id = validated_data.get('timeslot_id', instance.timeslot_id)
        instance.title = validated_data.get('title', instance.title)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.summary = validated_data.get('summary', instance.summary)
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.status = validated_data.get('status', instance.status)
        instance.cba_id = validated_data.get('cba_id', instance.cba_id)
        instance.save()
        return instance