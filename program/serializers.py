from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from rest_framework import serializers, status
from rest_framework.response import Response
from program.models import Show, Schedule, TimeSlot, Category, RTRCategory, Host, Language, Topic, MusicFocus, Note, Type, Language, RRule
from profile.models import Profile
from profile.serializers import ProfileSerializer
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    # Add profile fields to JSON
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = '__all__'


    def create(self, validated_data):
        """
        Create and return a new User instance, given the validated data.
        """

        profile_data = validated_data.pop('profile')

        user = super(UserSerializer, self).create(validated_data)
        user.date_joined = datetime.today()
        user.set_password(validated_data['password'])
        user.save()

        profile = Profile(user=user, cba_username=profile_data.get('cba_username').strip(), cba_user_token=profile_data.get('cba_user_token').strip())
        profile.save()

        return user


    def update(self, instance, validated_data):
        """
        Update and return an existing User instance, given the validated data.
        """

        user = self.context['user']

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)

        if user.is_superuser:
            instance.groups = validated_data.get('groups', instance.groups)
            instance.user_permissions = validated_data.get('user_permissions', instance.user_permissions)
            instance.is_active = validated_data.get('is_active', instance.is_active)
            instance.is_staff = validated_data.get('is_staff', instance.is_staff)
            instance.is_superuser = validated_data.get('is_superuser', instance.is_superuser)

        # TODO: How to hook into this from ProfileSerializer without having to call it here?
        try:
            profile = Profile.objects.get(user=instance.id)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=instance, **validated_data['profile'])

        profile.cba_username = validated_data['profile'].get('cba_username')
        profile.cba_user_token = validated_data['profile'].get('cba_user_token')
        profile.save()

        instance.save()
        return instance



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


    def update(self, instance, validated_data):
        """
        Update and return an existing Category instance, given the validated data.
        """
        instance.category = validated_data.get('category', instance.category)
        instance.abbrev = validated_data.get('abbrev', instance.abbrev)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.color = validated_data.get('color', instance.color)
        instance.description = validated_data.get('description', instance.description)

        instance.save()
        return instance


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'


    def update(self, instance, validated_data):
        """
        Update and return an existing Host instance, given the validated data.
        """

        instance.name = validated_data.get('name', instance.name)
        instance.is_always_visible = validated_data.get('is_always_visible', instance.is_always_visible)
        instance.email = validated_data.get('email', instance.email)
        instance.website = validated_data.get('website', instance.website)
        instance.biography = validated_data.get('biography', instance.biography)
        instance.googleplus_url = validated_data.get('googleplus_url', instance.googleplus_url)
        instance.facebook_url = validated_data.get('facebook_url', instance.facebook_url)
        instance.twitter_url = validated_data.get('twitter_url', instance.twitter_url)
        instance.linkedin_url = validated_data.get('linkedin_url', instance.linkedin_url)
        instance.youtube_url = validated_data.get('youtube_url', instance.youtube_url)
        instance.dorftv_url = validated_data.get('dorftv_url', instance.dorftv_url)
        instance.cba_url = validated_data.get('cba_url', instance.cba_url)
        instance.image = validated_data.get('image', instance.image)

        instance.save()
        return instance


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


    def update(self, instance, validated_data):
        """
        Update and return an existing Language instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)

        instance.save()
        return instance


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


    def update(self, instance, validated_data):
        """
        Update and return an existing Topic instance, given the validated data.
        """
        instance.topic = validated_data.get('topic', instance.topic)
        instance.abbrev = validated_data.get('abbrev', instance.abbrev)
        instance.slug = validated_data.get('slug', instance.slug)

        instance.save()
        return instance


class MusicFocusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicFocus
        fields = '__all__'


    def update(self, instance, validated_data):
        """
        Update and return an existing MusicFocus instance, given the validated data.
        """
        instance.focus = validated_data.get('focus', instance.focus)
        instance.abbrev = validated_data.get('abbrev', instance.abbrev)
        instance.slug = validated_data.get('slug', instance.slug)

        instance.save()
        return instance


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


    def update(self, instance, validated_data):
        """
        Update and return an existing Type instance, given the validated data.
        """
        instance.type = validated_data.get('type', instance.type)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.color = validated_data.get('color', instance.color)
        instance.text_color = validated_data.get('text_color', instance.text_color)
        instance.enabled = validated_data.get('enabled', instance.enabled)

        instance.save()
        return instance


class RTRCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RTRCategory
        fields = '__all__'


    def update(self, instance, validated_data):
        """
        Update and return an existing RTRCategory instance, given the validated data.
        """
        instance.rtrcategory = validated_data.get('rtrcategory', instance.rtrcategory)
        instance.abbrev = validated_data.get('abbrev', instance.abbrev)
        instance.slug = validated_data.get('slug', instance.slug)

        instance.save()
        return instance


class ShowSerializer(serializers.HyperlinkedModelSerializer):
    owners = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),many=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(),many=True)
    hosts = serializers.PrimaryKeyRelatedField(queryset=Host.objects.all(),many=True)
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all(),many=True)
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(),many=True)
    musicfocus = serializers.PrimaryKeyRelatedField(queryset=MusicFocus.objects.all(),many=True)
    type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all())
    rtrcategory = serializers.PrimaryKeyRelatedField(queryset=RTRCategory.objects.all())

    class Meta:
        model = Show
        fields = ('id', 'name', 'slug', 'image', 'logo', 'short_description', 'description',
                  'email', 'website', 'created', 'last_updated', 'type', 'rtrcategory',
                  'predecessor_id', 'cba_series_id', 'fallback_id', 'category', 'hosts',
                  'owners', 'language', 'topic', 'musicfocus')


    def create(self, validated_data):
        """
        Create and return a new Show instance, given the validated data.
        """
        owners = validated_data.pop('owners')
        category = validated_data.pop('category')
        hosts = validated_data.pop('hosts')
        language = validated_data.pop('language')
        topic = validated_data.pop('topic')
        musicfocus = validated_data.pop('musicfocus')

        show = Show.objects.create(**validated_data)

        # Save many-to-many relationships
        show.owners = owners
        show.category = category
        show.hosts = hosts
        show.language = language
        show.topic = topic
        show.musicfocus = musicfocus

        show.save()
        return show


    def update(self, instance, validated_data):
        """
        Update and return an existing Show instance, given the validated data.
        """

        user = self.context['user']

        instance.name = validated_data.get('name', instance.name)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.image = validated_data.get('image', instance.image)
        instance.logo = validated_data.get('logo', instance.logo)
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.description = validated_data.get('description', instance.description)
        instance.email = validated_data.get('email', instance.email)
        instance.website = validated_data.get('website', instance.website)
        instance.predecessor_id = validated_data.get('predecessor_id', instance.predecessor_id)
        instance.cba_series_id = validated_data.get('cba_series_id', instance.cba_series_id)
        instance.fallback_id = validated_data.get('fallback_id', instance.fallback_id)

        # Only superusers may update the following fields
        if user.is_superuser:
            instance.owners = validated_data.get('owners', instance.owners)
            instance.category = validated_data.get('category', instance.category)
            instance.hosts = validated_data.get('hosts', instance.hosts)
            instance.language = validated_data.get('language', instance.language)
            instance.topic = validated_data.get('topic', instance.topic)
            instance.musicfocus = validated_data.get('musicfocus', instance.musicfocus)
            instance.type = validated_data.get('type', instance.type)
            instance.rtrcategory = validated_data.get('rtrcategory', instance.rtrcategory)

        instance.save()
        return instance


# TODO: collision detection
class ScheduleSerializer(serializers.ModelSerializer):
    rrule = serializers.PrimaryKeyRelatedField(queryset=RRule.objects.all())
    show = serializers.PrimaryKeyRelatedField(queryset=Show.objects.all())

    class Meta:
        model = Schedule
        fields = '__all__'

    def create(self, validated_data):
        """Create and return a new Schedule instance, given the validated data."""

        rrule = validated_data.pop('rrule')
        show = validated_data.pop('show')

        schedule = Schedule.objects.create(**validated_data)
        schedule.rrule = rrule
        schedule.show = show

        schedule.save()
        return schedule


    def update(self, instance, validated_data):
        """Update and return an existing Schedule instance, given the validated data."""

        instance.byweekday = validated_data.get('byweekday', instance.byweekday)
        instance.dstart = validated_data.get('dstart', instance.dstart)
        instance.tstart = validated_data.get('tstart', instance.tstart)
        instance.tend = validated_data.get('tend', instance.tend)
        instance.until = validated_data.get('until', instance.until)
        instance.is_repetition = validated_data.get('is_repetition', instance.is_repetition)
        instance.fallback_id = validated_data.get('fallback_id', instance.fallback_id)
        instance.automation_id = validated_data.get('automation_id', instance.automation_id)
        instance.rrule = validated_data.get('rrule', instance.rrule)
        instance.show = validated_data.get('show', instance.show)

        instance.save()
        return instance


class TimeSlotSerializer(serializers.ModelSerializer):
    show = serializers.PrimaryKeyRelatedField(queryset=Show.objects.all())
    schedule = serializers.PrimaryKeyRelatedField(queryset=Schedule.objects.all())

    class Meta:
        model = TimeSlot
        fields = '__all__'

    def create(self, validated_data):
        """Create and return a new TimeSlot instance, given the validated data."""
        return TimeSlot.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """Update and return an existing Show instance, given the validated data."""

        # Only save certain fields
        instance.memo = validated_data.get('memo', instance.memo)
        instance.is_repetition = validated_data.get('is_repetition', instance.is_repetition)
        instance.playlist_id = validated_data.get('playlist_id', instance.playlist_id)
        instance.save()
        return instance


class NoteSerializer(serializers.ModelSerializer):
    show = serializers.PrimaryKeyRelatedField(queryset=Show.objects.all())
    timeslot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())
    host = serializers.PrimaryKeyRelatedField(queryset=Host.objects.all())

    class Meta:
        model = Note
        fields = '__all__'


    def create(self, validated_data):
        """Create and return a new Note instance, given the validated data."""

        # Save the creator
        validated_data['user_id'] = self.context['user_id']

        # Try to retrieve audio URL from CBA
        validated_data['audio_url'] = Note.get_audio_url(validated_data['cba_id'])

        return Note.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """Update and return an existing Note instance, given the validated data."""

        instance.show = validated_data.get('show', instance.show)
        instance.timeslot = validated_data.get('timeslot', instance.timeslot)
        instance.title = validated_data.get('title', instance.title)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.summary = validated_data.get('summary', instance.summary)
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.status = validated_data.get('status', instance.status)
        instance.host = validated_data.get('host', instance.host)
        instance.cba_id = validated_data.get('cba_id', instance.cba_id)
        instance.audio_url = Note.get_audio_url(instance.cba_id)

        instance.save()
        return instance