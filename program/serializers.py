from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.response import Response
from program.models import Show, Schedule, TimeSlot, Category, RTRCategory, Host, Language, Topic, MusicFocus, Note, Type, Language
from profile.models import Profile
from profile.serializers import ProfileSerializer


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

        profile = Profile(user=user, cba_username=profile_data.get('cba_username'), cba_user_token=profile_data.get('cba_user_token'))
        profile.save()

        return user


    def update(self, instance, validated_data):
        """
        Update and return an existing User instance, given the validated data.
        """

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)

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

        # TODO: Still put this into a sub app?
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


'''
class OwnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owners
        fields = '__all__'
'''


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


# TODO: collision detection
class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new Schedule instance, given the validated data.
        """
        return Schedule.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """
        Update and return an existing Schedule instance, given the validated data.
        """
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