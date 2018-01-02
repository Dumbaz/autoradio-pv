import json
from datetime import date, datetime, time, timedelta

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from program.models import Type, MusicFocus, Language, Note, Show, Category, RTRCategory, Topic, TimeSlot, Host, Schedule
from program.serializers import TypeSerializer, LanguageSerializer, MusicFocusSerializer, NoteSerializer, ShowSerializer, ScheduleSerializer, CategorySerializer, RTRCategorySerializer, TopicSerializer, TimeSlotSerializer, HostSerializer, UserSerializer
from program.utils import tofirstdayinisoweek, get_cached_shows


class CalendarView(TemplateView):
    template_name = 'calendar.html'


class HostListView(ListView):
    context_object_name = 'host_list'
    queryset = Host.objects.filter(Q(is_always_visible=True) | Q(shows__schedules__until__gt=datetime.now())).distinct()
    template_name = 'host_list.html'


class HostDetailView(DetailView):
    context_object_name = 'host'
    queryset = Host.objects.all()
    template_name = 'host_detail.html'


class ShowListView(ListView):
    context_object_name = 'show_list'
    template_name = 'show_list.html'

    def get_queryset(self):
        queryset = Show.objects.filter(schedules__until__gt=date.today()).exclude(id=1).distinct()
        if 'type' in self.request.GET:
            type = get_object_or_404(Type, slug=self.request.GET['type'])
            queryset = queryset.filter(type=type)
        elif 'musicfocus' in self.request.GET:
            musicfocus = get_object_or_404(MusicFocus, slug=self.request.GET['musicfocus'])
            queryset = queryset.filter(musicfocus=musicfocus)
        elif 'category' in self.request.GET:
            category = get_object_or_404(Category, slug=self.request.GET['category'])
            queryset = queryset.filter(category=category)
        elif 'topic' in self.request.GET:
            topic = get_object_or_404(Topic, slug=self.request.GET['topic'])
            queryset = queryset.filter(topic=topic)
        elif 'rtrcategory' in self.request.GET:
            rtrcategory = get_object_or_404(RTRCategory, slug=self.request.GET['rtrcategory'])
            queryset = queryset.filter(rtrcategory=rtrcategory)


        return queryset


class ShowDetailView(DetailView):
    queryset = Show.objects.all().exclude(id=1)
    template_name = 'show_detail.html'


class TimeSlotDetailView(DetailView):
    queryset = TimeSlot.objects.all()
    template_name = 'timeslot_detail.html'


class RecommendationsListView(ListView):
    context_object_name = 'recommendation_list'
    template_name = 'recommendation_list.html'

    now = datetime.now()
    end = now + timedelta(weeks=1)

    queryset = TimeSlot.objects.filter(Q(note__isnull=False, note__status=1,
                                         start__range=(now, end)) |
                                       Q(show__type__slug='sondersendung',
                                         start__range=(now, end))).order_by('start')[:20]


class RecommendationsBoxView(RecommendationsListView):
    template_name = 'boxes/recommendation.html'


class DayScheduleView(TemplateView):
    template_name = 'day_schedule.html'

    def get_context_data(self, **kwargs):
        year = self.kwargs.get('year', None)
        month = self.kwargs.get('month', None)
        day = self.kwargs.get('day', None)

        if year is None and month is None and day is None:
            today = datetime.combine(date.today(), time(6, 0))
        else:
            today = datetime.strptime('%s__%s__%s__06__00' % (year, month, day), '%Y__%m__%d__%H__%M')

        tomorrow = today + timedelta(days=1)

        context = super(DayScheduleView, self).get_context_data(**kwargs)
        context['day'] = today
        context['recommendations'] = Note.objects.filter(status=1, timeslot__start__range=(today, tomorrow))
        context['default_show'] = Show.objects.get(pk=1)

        timeslots = TimeSlot.objects.get_day_timeslots(today)

        if 'type' in self.request.GET:
            type = get_object_or_404(Type, slug=self.request.GET['type'])
            context['timeslots'] = timeslots.filter(show__type=type)
        elif 'musicfocus' in self.request.GET:
            musicfocus = get_object_or_404(MusicFocus, slug=self.request.GET['musicfocus'])
            context['timeslots'] = timeslots.filter(show__musicfocus=musicfocus)
        elif 'category' in self.request.GET:
            category = get_object_or_404(Category, slug=self.request.GET['category'])
            context['timeslots'] = timeslots.filter(show__category=category)
        elif 'topic' in self.request.GET:
            topic = get_object_or_404(Topic, slug=self.request.GET['topic'])
            context['topic'] = timeslots.filter(show__topic=topic)
        else:
            context['timeslots'] = timeslots
        return context


class CurrentShowBoxView(TemplateView):
    context_object_name = 'recommendation_list'
    template_name = 'boxes/current.html'

    def get_context_data(self, **kwargs):
        current_timeslot = TimeSlot.objects.get_or_create_current()
        previous_timeslot = current_timeslot.get_previous_by_start()
        next_timeslot = current_timeslot.get_next_by_start()
        after_next_timeslot = next_timeslot.get_next_by_start()

        context = super(CurrentShowBoxView, self).get_context_data(**kwargs)
        context['current_timeslot'] = current_timeslot
        context['previous_timeslot'] = previous_timeslot
        context['next_timeslot'] = next_timeslot
        context['after_next_timeslot'] = after_next_timeslot
        return context


class WeekScheduleView(TemplateView):
    template_name = 'week_schedule.html'

    def get_context_data(self, **kwargs):
        year = self.kwargs.get('year', None)
        week = self.kwargs.get('week', None)

        if year is None and week is None:
            year, week = datetime.now().strftime('%G__%V').split('__')

        monday = tofirstdayinisoweek(int(year), int(week))
        tuesday = monday + timedelta(days=1)
        wednesday = monday + timedelta(days=2)
        thursday = monday + timedelta(days=3)
        friday = monday + timedelta(days=4)
        saturday = monday + timedelta(days=5)
        sunday = monday + timedelta(days=6)

        context = super(WeekScheduleView, self).get_context_data()
        context['monday'] = monday
        context['tuesday'] = tuesday
        context['wednesday'] = wednesday
        context['thursday'] = thursday
        context['friday'] = friday
        context['saturday'] = saturday
        context['sunday'] = sunday
        context['default_show'] = Show.objects.get(pk=1)
        context['monday_timeslots'] = TimeSlot.objects.get_day_timeslots(monday)
        context['tuesday_timeslots'] = TimeSlot.objects.get_day_timeslots(tuesday)
        context['wednesday_timeslots'] = TimeSlot.objects.get_day_timeslots(wednesday)
        context['thursday_timeslots'] = TimeSlot.objects.get_day_timeslots(thursday)
        context['friday_timeslots'] = TimeSlot.objects.get_day_timeslots(friday)
        context['saturday_timeslots'] = TimeSlot.objects.get_day_timeslots(saturday)
        context['sunday_timeslots'] = TimeSlot.objects.get_day_timeslots(sunday)
        context['last_w'] = datetime.strftime(monday - timedelta(days=7), '%G/%V')
        context['cur_w'] = datetime.strftime(monday, '%G/%V')
        context['next_w1'] = datetime.strftime(monday + timedelta(days=7), '%G/%V')
        context['next_w2'] = datetime.strftime(monday + timedelta(days=14), '%G/%V')
        context['next_w3'] = datetime.strftime(monday + timedelta(days=21), '%G/%V')
        context['next_w4'] = datetime.strftime(monday + timedelta(days=28), '%G/%V')
        return context


class StylesView(TemplateView):
    template_name = 'styles.css'
    content_type = 'text/css'

    def get_context_data(self, **kwargs):
        context = super(StylesView, self).get_context_data(**kwargs)
        context['types'] = Type.objects.filter(enabled=True)
        context['musicfocus'] = MusicFocus.objects.all()
        context['category'] = Category.objects.all()
        context['topic'] = Topic.objects.all()
        return context


def json_day_schedule(request, year=None, month=None, day=None):
    if year is None and month is None and day is None:
        today = datetime.combine(date.today(), time(0, 0))
    else:
        today = datetime.strptime('%s__%s__%s__00__00' % (year, month, day), '%Y__%m__%d__%H__%M')

    timeslots = TimeSlot.objects.get_24h_timeslots(today).select_related('schedule').select_related('show')
    schedule = []
    for ts in timeslots:
        entry = {
            'start': ts.start.strftime('%Y-%m-%d_%H:%M:%S'),
            'end': ts.end.strftime('%Y-%m-%d_%H:%M:%S'),
            'title': ts.show.name,
            'id': ts.show.id,
            'automation-id': -1
        }

        if ts.schedule.automation_id:
            entry['automation-id'] = ts.schedule.automation_id

        schedule.append(entry)

    return HttpResponse(json.dumps(schedule, ensure_ascii=False).encode('utf8'),
                        content_type="application/json; charset=utf-8")


def json_week_schedule(request):
    """
    Called by calendar to get all timeslots for a week.
    Expects GET variable 'start' (date), otherwise start will be today
    Returns all timeslots of the next 7 days
    """

    if request.GET.get('start') == None:
        start = datetime.combine(date.today(), time(0, 0))
    else:
        start = datetime.combine( datetime.strptime(request.GET.get('start'), '%Y-%m-%d').date(), time(0, 0))

    timeslots = TimeSlot.objects.get_7d_timeslots(start).select_related('schedule').select_related('show')
    schedule = []
    for ts in timeslots:

        is_repetition = ' ' + _('REP') if ts.schedule.is_repetition is 1 else ''

        hosts = ', '.join(ts.show.hosts.values_list('name', flat=True))
        categories = ', '.join(ts.show.category.values_list('category', flat=True))
        topics = ', '.join(ts.show.topic.values_list('topic', flat=True))
        musicfocus = ', '.join(ts.show.musicfocus.values_list('focus', flat=True))
        languages = ', '.join(ts.show.language.values_list('name', flat=True))
        rtrcategory = RTRCategory.objects.get(pk=ts.show.rtrcategory_id)
        type = Type.objects.get(pk=ts.show.type_id)

        classname = 'default'

        if ts.playlist_id is None or ts.playlist_id == 0:
            classname = 'danger'

        entry = {
            'id': ts.id,
            'start': ts.start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': ts.end.strftime('%Y-%m-%dT%H:%M:%S'),
            'title': ts.show.name + is_repetition, # For JS Calendar
            'automation-id': -1,
            'schedule_id': ts.schedule.id,
            'is_repetition': ts.is_repetition,
            'playlist_id': ts.playlist_id,
            'schedule_fallback_id': ts.schedule.fallback_playlist_id, # The schedule's fallback
            'show_fallback_id': ts.show.fallback_pool, # The show's fallback
            'show_id': ts.show.id,
            'show_name': ts.show.name + is_repetition,
            'show_hosts': hosts,
            'show_type': type.type,
            'show_categories': categories,
            'show_topics': topics,
            'show_musicfocus': musicfocus,
            'show_languages': languages,
            'show_rtrcategory': rtrcategory.rtrcategory,
            'station_fallback_id': 0, # TODO: The station's global fallback (might change)
            'memo': ts.memo,
            'className': classname,
        }

        if ts.schedule.automation_id:
            entry['automation-id'] = ts.schedule.automation_id

        schedule.append(entry)

    return HttpResponse(json.dumps(schedule, ensure_ascii=False).encode('utf8'),
                        content_type="application/json; charset=utf-8")


def json_timeslots_specials(request):
    specials = {}
    shows = get_cached_shows()['shows']
    for show in shows:
        show['pv_id'] = -1
        if show['type'] == 's':
            specials[show['id']] = show

    for ts in TimeSlot.objects.filter(end__gt=datetime.now(),
                                      schedule__automation_id__in=specials.iterkeys()).select_related('show'):
        automation_id = ts.schedule.automation_id
        start = ts.start.strftime('%Y-%m-%d_%H:%M:%S')
        end = ts.end.strftime('%Y-%m-%d_%H:%M:%S')
        if specials[automation_id]['pv_id'] != -1:
            if specials[automation_id]['pv_start'] < start:
                continue

        specials[automation_id]['pv_id'] = int(ts.show.id)
        specials[automation_id]['pv_name'] = ts.show.name
        specials[automation_id]['pv_start'] = start
        specials[automation_id]['pv_end'] = end

    return HttpResponse(json.dumps(specials, ensure_ascii=False).encode('utf8'),
                        content_type="application/json; charset=utf-8")




####################################################################
# REST API View Sets
####################################################################


class APIUserViewSet(viewsets.ModelViewSet):
    """
    /api/v1/users   Returns oneself - Superusers see all users. Only superusers may create a user (GET, POST)
    /api/v1/users/1 Used for retrieving or updating a single user. Non-superusers may only update certain fields. (GET, PUT) - DELETE is prohibited for everyone

    Superusers may access and update all users
    """

    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = UserSerializer
    queryset = User.objects.none()
    required_scopes = ['users']


    def get_queryset(self):
        """Constrain access to oneself except for superusers"""
        if self.request.user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(pk=self.request.user.id)


    def list(self, request):
        users = self.get_queryset()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        """Returns a single user"""

        # Common users only see themselves
        if not request.user.is_superuser and int(pk) != request.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


    def create(self, request, pk=None):
        """
        Create a User
        Only superusers may create a user
        """

        if not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None):

        # Common users may only edit themselves
        if not request.user.is_superuser and int(pk) != request.user.id:
            return Response(serializer.initial_data, status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, context={ 'user': request.user })

        if serializer.is_valid():
            serializer.save();
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        """Deleting users is prohibited: Set 'is_active' to False instead"""
        return Response(status=status.HTTP_401_UNAUTHORIZED)



class APIShowViewSet(viewsets.ModelViewSet):
    """
    /api/v1/shows/                                             Returns shows a user owns (GET, POST)
    /api/v1/shows/?active=true                                 Returns all active shows (no matter if owned by user) (GET)
    /api/v1/shows/1                                            Used for retrieving a single show or update (if owned) (GET, PUT, DELETE)
    /api/v1/shows/1/notes                                      Returns all notes to the show (GET) - POST not allowed at this level, use /shows/1/schedules/1/timeslots/1/notes instead
    /api/v1/shows/1/notes/1                                    Returns the note of the show by its ID (GET) - PUT/DELETE not allowed at this level, use /shows/1/schedules/1/timeslots/1/notes/1/ instead
    /api/v1/shows/1/schedules                                  Returns all schedules of the show (GET, POST)
    /api/v1/shows/1/schedules/1                                Returns the schedule of the show by its ID (GET) - POST not allowed at this level, use /shows/1/schedules/ instead
    /api/v1/shows/1/timeslots                                  Returns all timeslots of the show (GET) - Timeslots may only be added by creating/updating a schedule
    /api/v1/shows/1/timeslots/1                                Returns the timeslot of the show (GET) - Timeslots may only be added by creating/updating a schedule
    /api/v1/shows/1/timeslots?start=2017-01-01&end=2017-12-31  Returns all timeslots of the show within the given timerange (GET)
    /api/v1/shows/1/timeslots/1/notes                          Returns all notes to the timeslot (one at max) (GET) - POST not allowed at this level, use /shows/1/schedules/1/timelots/1/notes/ instead
    /api/v1/shows/1/timeslots/1/notes/1                        Returns the note of the show's timeslot by its ID (GET) - PUT/DELETE not allowed at this level, use /shows/1/schedules/1/timeslots/1/notes/1/ instead

    Only superusers may add and delete shows
    """

    queryset = Show.objects.none()
    serializer_class = ShowSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['shows']


    def get_queryset(self):

        if self.request.GET.get('active') == 'true':
            '''Filter for retrieving currently running shows'''

            # Get currently running schedules to filter by
            # For single dates we test if there'll be one in the future (and ignore the until date)
            # TODO: Really consider dstart? (=currently active, not just upcoming ones)
            # Add limit for future?
            schedules = Schedule.objects.filter( Q(rrule_id__gt=1,dstart__lte=date.today(),until__gte=date.today()) |
                                                 Q(rrule_id=1,dstart__gte=date.today())
                                               ).distinct().values_list('show_id', flat=True)

            return Show.objects.filter(id__in=schedules)

        return Show.objects.all()


    def list(self, request):
        """List shows"""
        shows = self.get_queryset()
        serializer = ShowSerializer(shows, many=True)
        return Response(serializer.data)


    def create(self, request, pk=None):
        """
        Create a show
        Only superusers may create a show
        """

        if not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = ShowSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        """Returns a single show"""
        show = get_object_or_404(Show, pk=pk)
        serializer = ShowSerializer(show)
        return Response(serializer.data)


    def update(self, request, pk=None):
        """
        Update a show
        Common users may only update shows they own
        """

        if not Show.is_editable(self, pk):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        show = get_object_or_404(Show, pk=pk)
        serializer = ShowSerializer(show, data=request.data, context={ 'user': request.user })

        if serializer.is_valid():
            serializer.save();
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        """
        Delete a show
        Only superusers may delete shows
        """

        if not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        show = get_object_or_404(Show, pk=pk)
        Show.objects.delete(pk=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)



class APIScheduleViewSet(viewsets.ModelViewSet):
    """
    /api/v1/schedules/          Returns schedules (GET) - POST not allowed at this level
    /api/v1/schedules/1         Returns the given schedule (GET) - POST not allowed at this level
    /api/v1/shows/1/schedules   Returns schedules of the show (GET, POST)
    /api/v1/shows/1/schedules/1 Returns schedules by its ID (GET, PUT, DELETE)

    Only superusers may create and update schedules
    """

    queryset = Schedule.objects.none()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['schedules']


    def get_queryset(self):
        show_pk = self.kwargs['show_pk'] if 'show_pk' in self.kwargs else None

        if show_pk != None:
            return Schedule.objects.filter(show=show_pk)

        return Schedule.objects.all()


    def list(self, request, show_pk=None, pk=None):
        """List Schedules of a show"""
        schedules = self.get_queryset()
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None, show_pk=None):

        if show_pk != None:
            schedule = get_object_or_404(Schedule, pk=pk, show=show_pk)
        else:
            schedule = get_object_or_404(Schedule, pk=pk)

        serializer = ScheduleSerializer(schedule)
        return Response(serializer.data)


    def create(self, request, show_pk=None, pk=None):
        """
        TODO: Create a schedule, generate timeslots, test for collisions and resolve them including notes
        Only superusers may add schedules
        """

        # Only allow creating when calling /shows/1/schedules/1
        if show_pk == None or not request.user.is_superuser:
            return Response(status=HTTP_401_UNAUTHORIZED)

        return Response(status=HTTP_401_UNAUTHORIZED)


    def update(self, request, pk=None, show_pk=None):
        """
        TODO: Update a schedule, generate timeslots, test for collisions and resolve them including notes
        Only superusers may update schedules
        """

        # Only allow updating when calling /shows/1/schedules/1
        if show_pk == None or not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        schedule = get_object_or_404(Schedule, pk=pk, show=show_pk)

        serializer = ScheduleSerializer(schedule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        """
        Delete a schedule
        Only superusers may delete schedules
        """

        if not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        schedule = get_object_or_404(Schedule, pk=pk)
        Schedule.objects.delete(pk=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)



class APITimeSlotViewSet(viewsets.ModelViewSet):
    """
    /api/v1/timeslots                                                     Returns timeslots of the next 60 days (GET) - Timeslots may only be added by creating/updating a schedule
    /api/v1/timeslots/1                                                   Returns the given timeslot (GET) - PUT/DELETE not allowed at this level
    /api/v1/timeslots/?start=2017-01-01&end=2017-02-01                    Returns timeslots within the given timerange (GET)
    /api/v1/shows/1/timeslots                                             Returns timeslots of the show (GET, POST)
    /api/v1/shows/1/timeslots/1                                           Returns a timeslots by its ID (GET, PUT, DELETE)
    /api/v1/shows/1/timeslots?start=2017-01-01&end=2017-02-01             Returns timeslots of the show within the given timerange
    /api/v1/shows/1/schedules/1/timeslots                                 Returns all timeslots of the schedule (GET, POST)
    /api/v1/shows/1/schedules/1/timeslots/1                               Returns a timeslot by its ID (GET, PUT, DELETE)
    /api/v1/shows/1/schedules/1/timeslots?start=2017-01-01&end=2017-02-01 Returns all timeslots of the schedule within the given timerange
    """

    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = TimeSlotSerializer
    queryset = TimeSlot.objects.none()
    required_scopes = ['timeslots']


    def get_queryset(self):
        show_pk = self.kwargs['show_pk'] if 'show_pk' in self.kwargs else None
        schedule_pk = self.kwargs['schedule_pk'] if 'schedule_pk' in self.kwargs else None

        # Return next 60 days by default
        start = datetime.combine(date.today(), time(0, 0))
        end = start + timedelta(days=60)

        if self.request.GET.get('start') and self.request.GET.get('end'):
            start = datetime.combine( datetime.strptime(self.request.GET.get('start'), '%Y-%m-%d').date(), time(0, 0))
            end = datetime.combine( datetime.strptime(self.request.GET.get('end'), '%Y-%m-%d').date(), time(23, 59))

        # If show is given: Return corresponding timeslots
        if show_pk != None and schedule_pk != None:
            # /shows/1/schedules/1/timeslots/ returns timeslots of the given schedule and show
            return TimeSlot.objects.filter(show=show_pk, schedule=schedule_pk, start__gte=start, end__lte=end).order_by('start')
        elif show_pk != None and schedule_pk == None:
            # /shows/1/timeslots returns timeslots of the show
            return TimeSlot.objects.filter(show=show_pk, start__gte=start, end__lte=end).order_by('start')
        else:
            # Otherwise return all timeslots
            return TimeSlot.objects.filter(start__gte=start, end__lte=end).order_by('start')


    def list(self, request, show_pk=None, schedule_pk=None):
        """Lists timeslots of a show"""
        timeslots = self.get_queryset()
        serializer = TimeSlotSerializer(timeslots, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None, schedule_pk=None, show_pk=None):

        if show_pk != None:
            timeslot = get_object_or_404(TimeSlot, pk=pk, show=show_pk)
        else:
            timeslot = get_object_or_404(TimeSlot, pk=pk)

        serializer = TimeSlotSerializer(timeslot)
        return Response(serializer.data)


    def create(self, request):
        """
        Timeslots may only be created by adding/updating schedules
        TODO: Adding single timeslot which fits to schedule?
        """
        return Response(status=HTTP_401_UNAUTHORIZED)


    def update(self, request, pk=None, schedule_pk=None, show_pk=None):
        """Link a playlist_id to a timeslot"""

        timeslot = get_object_or_404(TimeSlot, pk=pk, schedule=schedule_pk, show=show_pk)

        # Update is only allowed when calling /shows/1/schedules/1/timeslots/1 and if user owns the show
        if schedule_pk == None or show_pk==None or not Show.is_editable(self, timeslot.show_id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = TimeSlotSerializer(timeslot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        """
        Delete a timeslot
        Only superusers may delete timeslots
        """

        if not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        timeslot = get_object_or_404(TimeSlot, pk=pk)
        TimeSlot.objects.delete(pk=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)



class APINoteViewSet(viewsets.ModelViewSet):
    """
    /api/v1/notes/                                  Returns all notes (GET) - POST not allowed at this level
    /ap1/v1/notes/1                                 Returns a single note (if owned) (GET) - PUT/DELETE not allowed at this level
    /api/v1/notes/?ids=1,2,3,4,5                    Returns given notes (if owned) (GET)
    /api/v1/shows/1/notes                           Returns all notes of a show (GET) - POST not allowed at this level
    /api/v1/shows/1/notes/1                         Returns a note by its ID (GET) - PUT/DELETE not allowed at this level
    /api/v1/shows/1/timeslots/1/notes/              Returns a note of the timeslot (GET) - POST not allowed at this level
    /api/v1/shows/1/timeslots/1/notes/1             Returns a note by its ID (GET) - PUT/DELETE not allowed at this level
    /api/v1/shows/1/schedules/1/timeslots/1/notes   Returns a note to the timeslot (GET, POST) - Only one note allowed per timeslot
    /api/v1/shows/1/schedules/1/timeslots/1/notes/1 Returns a note by its ID (GET, PUT, DELETE)

    Superusers may access and update all notes
    """

    queryset = Note.objects.none()
    serializer_class = NoteSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['notes']


    def get_queryset(self):

        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None
        timeslot_pk = self.kwargs['timeslot_pk'] if 'timeslot_pk' in self.kwargs else None
        show_pk = self.kwargs['show_pk'] if 'show_pk' in self.kwargs else None

        # TODO: Should users be able to edit other's notes if they're part of a show they own?
        if self.request.GET.get('ids') != None:
            note_ids = self.request.GET.get('ids').split(',')
            if self.request.user.is_superuser:
                notes = Note.objects.filter(id__in=note_ids)
            else:
                # Common users only retrieve notes they own
                notes = Note.objects.filter(id__in=note_ids,user=self.request.user.id)
        else:

            if show_pk != None and timeslot_pk != None:
                # /shows/1/schedules/1/timeslots/1/notes
                # /shows/1/timeslots/1/notes/
                # ...return notes to the timeslot
                notes = Note.objects.filter(show=show_pk, timeslot=timeslot_pk)
            elif show_pk != None and timeslot_pk == None:
                # /shows/1/notes returns notes to the show
                notes = Note.objects.filter(show=show_pk)
            else:
                # /notes returns all notes
                notes = Note.objects.all()
                #notes = Note.objects.filter(user=self.request.user.id)

        return notes


    def list(self, request, pk=None, timeslot_pk=None, schedule_pk=None, show_pk=None):
        """Lists notes"""
        notes = self.get_queryset()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)


    def create(self, request, pk=None, timeslot_pk=None, schedule_pk=None, show_pk=None):
        """Create a note"""

        # Only create a note if show_id, timeslot_id and schedule_id is given
        if show_pk == None or schedule_pk == None or timeslot_pk == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not Show.is_editable(self, show_pk):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = NoteSerializer(data=request.data, context={ 'user_id': request.user.id })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None, timeslot_pk=None, schedule_pk=None, show_pk=None):
        """
        Returns a single note

        Called by:
        /notes/1
        /shows/1/notes/1
        /shows/1/timeslots/1/notes/1
        /shows/1/schedules/1/timeslots/1/notes/1
        """

        if show_pk != None and timeslot_pk == None and schedule_pk == None:
            # /shows/1/notes/1
            note = get_object_or_404(Note, pk=pk, show=show_pk)
        elif show_pk != None and timeslot_pk != None:
            # /shows/1/timeslots/1/notes/1
            # /shows/1/schedules/1/timeslots/1/notes/1
            note = get_object_or_404(Note, pk=pk, show=show_pk, timeslot=timeslot_pk)
        else:
            # /notes/1
            note = get_object_or_404(Note, pk=pk)

        serializer = NoteSerializer(note)
        return Response(serializer.data)


    def update(self, request, pk=None, show_pk=None, schedule_pk=None, timeslot_pk=None):

        # Allow PUT only when calling /shows/1/schedules/1/timeslots/1/notes/1
        if show_pk == None or schedule_pk == None or timeslot_pk == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        note = get_object_or_404(Note, pk=pk, timeslot=timeslot_pk, show=show_pk)

        # Commons users may only edit their own notes
        if not request.user.is_superuser and note.user_id != request.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = NoteSerializer(note, data=request.data)

        if serializer.is_valid():
            serializer.save();
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        note = get_object_or_404(Note, pk=pk)

        # Commons users may only delete their own notes
        if not request.user.is_superuser and note.user_id != request.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        Note.objects.delete(pk=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)



class APICategoryViewSet(viewsets.ModelViewSet):
    """
    /api/v1/categories/  Returns all categories (GET, POST)
    /api/v1/categories/1 Returns a category by its ID (GET, PUT, DELETE)
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['categories']



class APITypeViewSet(viewsets.ModelViewSet):
    """
    /api/v1/types/  Returns all types (GET, POST)
    /api/v1/types/1 Returns a type by its ID (GET, PUT, DELETE)
    """

    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['types']



class APITopicViewSet(viewsets.ModelViewSet):
    """
    /api/v1/topics/  Returns all topics (GET, POST)
    /api/v1/topics/1 Returns a topic by its ID (GET, PUT, DELETE)
    """

    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['topics']



class APIMusicFocusViewSet(viewsets.ModelViewSet):
    """
    /api/v1/musicfocus/  Returns all musicfocuses (GET, POST)
    /api/v1/musicfocus/1 Returns a musicfocus by its ID (GET, PUT, DELETE)
    """

    queryset = MusicFocus.objects.all()
    serializer_class = MusicFocusSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['musicfocus']



class APIRTRCategoryViewSet(viewsets.ModelViewSet):
    """
    /api/v1/rtrcategories/  Returns all rtrcategories (GET, POST)
    /api/v1/rtrcategories/1 Returns a rtrcategory by its ID (GET, PUT, DELETE)
    """

    queryset = RTRCategory.objects.all()
    serializer_class = RTRCategorySerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['rtrcategories']


class APILanguageViewSet(viewsets.ModelViewSet):
    """
    /api/v1/languages/  Returns all languages (GET, POST)
    /api/v1/languages/1 Returns a language by its ID (GET, PUT, DELETE)
    """

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['languages']


class APIHostViewSet(viewsets.ModelViewSet):
    """
    /api/v1/hosts/  Returns all hosts (GET, POST)
    /api/v1/hosts/1 Returns a host by its ID (GET, PUT, DELETE)
    """

    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['hosts']


'''
class APIOwnersViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = Owners.objects.all()
    serializer_class = OwnersSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    required_scopes = ['owners']
'''