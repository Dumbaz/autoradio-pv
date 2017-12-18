import json
from datetime import date, datetime, time, timedelta

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import detail_route

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
    /api/v1/users   Returns oneself - Superusers see all users
    /api/v1/users/1 Used for retrieving or updating a single user

    Superusers may access and update all users
    """

    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
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
        user = get_object_or_404(User, pk=pk)

        # Common users may only see themselves
        if not request.user.is_superuser and user.id != request.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(user)
        return Response(serializer.data)


    def partial_update(self, request, pk=None):

        # Common users may only edit themselves
        if not request.user.is_superuser and int(pk) != request.user.id:
            return Response(serializer.initial_data, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save();
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class APIShowViewSet(viewsets.ModelViewSet):
    """
    /api/v1/shows/                                             Returns shows a user owns
    /api/v1/shows/?active=true                                 Returns all active shows (no matter if owned by user)
    /api/v1/shows/1                                            Used for retrieving a single show or update (if owned)
    /api/v1/shows/1/schedules                                  Returns all schedules for the given show
    /api/v1/shows/1/timeslots                                  Returns all timeslots for the given show
    /api/v1/shows/1/timeslots?start=2017-01-01&end=2017-12-31  Returns all timeslots for the given show

    Superusers may access and update all shows
    """

    queryset = Show.objects.none()
    serializer_class = ShowSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    required_scopes = ['shows']


    def get_queryset(self):
        """Constrain access to owners except for superusers"""

        if self.request.GET.get('active') == 'true':
            '''Filter for retrieving currently running shows'''

            # Get currently running schedules to filter by
            # For single dates we test if there'll be one in the future (and ignore the until date)
            # TODO: Really consider dstart? (=currently active, not just upcoming ones)
            schedules = Schedule.objects.filter( Q(rrule_id__gt=1,dstart__lte=date.today(),until__gte=date.today()) |
                                             Q(rrule_id=1,dstart__gte=date.today()) ).distinct().values_list('show_id', flat=True)

            return Show.objects.filter(id__in=schedules)

        if self.request.user.is_superuser:
            return Show.objects.all()
        else:
            return self.request.user.shows.all()


    @detail_route(methods=['get'], url_path='schedules')
    def schedules(self, request, pk=None):
        """Return all schedules of the show"""
        show = get_object_or_404(Show, pk=pk)
        schedules = Schedule.objects.filter(show=show)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)


    @detail_route(methods=['get'], url_path='timeslots')
    def timeslots(self, request, pk=None):
        """Return timeslots of the show for the next 60 days or the given timerange"""
        show = get_object_or_404(Show, pk=pk)

        # Return next 60 days by default
        start = datetime.combine(date.today(), time(0, 0))
        end = start + timedelta(days=60)

        if self.request.GET.get('start') and self.request.GET.get('end'):
            start = datetime.combine( datetime.strptime(self.request.GET.get('start'), '%Y-%m-%d').date(), time(0, 0))
            end = datetime.combine( datetime.strptime(self.request.GET.get('end'), '%Y-%m-%d').date(), time(23, 59))

        timeslots = TimeSlot.objects.filter(show=show, start__gte=start, end__lte=end).order_by('start')
        serializer = TimeSlotSerializer(timeslots, many=True)
        return Response(serializer.data)


    def list(self, request):
        """Lists shows"""
        shows = self.get_queryset()
        serializer = ShowSerializer(shows, many=True)
        return Response(serializer.data)


    def create(self, request):
        """Create is not allowed at the moment"""
        return Response(status=status.HTTP_401_UNAUTHORIZED)


    def retrieve(self, request, pk=None):
        """Returns a single show"""
        show = get_object_or_404(Show, pk=pk)
        serializer = ShowSerializer(show)
        return Response(serializer.data)


    def partial_update(self, request, pk=None):
        serializer = ShowSerializer(data=request.data)

        # For common user and not owner of show: Permission denied
        if not Show.is_editable(self, pk):
            return Response(serializer.initial_data, status=status.HTTP_401_UNAUTHORIZED)

        if serializer.is_valid():
            serializer.save();
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APITimeSlotViewSet(viewsets.ModelViewSet):
    """
    /api/v1/timeslots                                            Returns timeslots of the next 60 days
    /api/v1/timeslots/?start=2017-01-01&end=2017-02-01           Returns timeslots within the given timerange
    /api/v1/timeslots/?show_id=1                                 Returns upcoming timeslots of a show 60 days in the future
    /api/v1/timeslots/?show_id=1&start=2017-01-01&end=2017-02-01 Returns timeslots of a show within the given timerange
    """

    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    serializer_class = TimeSlotSerializer
    queryset = TimeSlot.objects.none()
    required_scopes = ['timeslots']


    def get_queryset(self):
        # Return next 60 days by default
        start = datetime.combine(date.today(), time(0, 0))
        end = start + timedelta(days=60)

        if self.request.GET.get('start') and self.request.GET.get('end'):
            start = datetime.combine( datetime.strptime(self.request.GET.get('start'), '%Y-%m-%d').date(), time(0, 0))
            end = datetime.combine( datetime.strptime(self.request.GET.get('end'), '%Y-%m-%d').date(), time(23, 59))

        # If show is given: Return corresponding timeslots
        if self.request.GET.get('show_id') != None:
            show_id = int(self.request.GET.get('show_id'))

            if not Show.is_editable(self, show_id):
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            return TimeSlot.objects.filter(show=show_id, start__gte=start, end__lte=end).order_by('start')

        # Otherwise return all show timeslots
        return TimeSlot.objects.filter(start__gte=start, end__lte=end).order_by('start')


    def list(self, request):
        """Lists timeslots of a show"""
        timeslots = self.get_queryset()
        serializer = TimeSlotSerializer(timeslots, many=True)
        return Response(serializer.data)


    def create(self, request):
        """Timeslots may only be created by adding/updating schedules"""
        return Response(status=HTTP_401_UNAUTHORIZED)


    def partial_update(self, request, pk=None):
        """Link a playlist_id to a timeslot"""

        serializer = TimeSlotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class APINoteViewSet(viewsets.ModelViewSet):
    """
    /api/v1/notes/                Returns all notes the user owns
    /ap1/v1/notes/1               Returns a single note (if owned)
    /api/v1/notes/?ids=1,2,3,4,5  Returns given notes (if owned)

    Superusers may access and update all notes
    """

    queryset = Note.objects.none()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    required_scopes = ['notes']


    def get_queryset(self):

        # TODO: Should users be able to edit other's notes if they're part of a show they own?
        if self.request.GET.get('ids') != None:
            note_ids = self.request.GET.get('ids').split(',')
            if self.request.user.is_superuser:
                notes = Note.objects.filter(id__in=note_ids)
            else:
                # Common users only retrieve notes they own
                notes = Note.objects.filter(id__in=note_ids,user=self.request.user.id)
        else:
           notes = Note.objects.filter(user=self.request.user.id)

        return notes


    def list(self, request):
        """Lists notes"""
        notes = self.get_queryset()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)


    def create(self, request):
        """
        Creates a note
        """

        # Only create a note if show_id and timeslot_id is given
        if request.POST.get('show') == None or request.POST.get('timeslot') == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not Show.is_editable(self, request.POST.get('show')):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        """Returns a single note"""

        note = get_object_or_404(Note, pk=pk)

        if not request.user.is_superuser and int(pk) not in self.get_queryset().values_list('id', flat=True):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = NoteSerializer(note)
        return Response(serializer.data)


    def partial_update(self, request, pk=None):
        note = get_object_or_404(Note, pk=pk)

        if not request.user.is_superuser and note.user_id != request.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = NoteSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save();
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        note = get_object_or_404(Note, pk=pk)

        if not request.user.is_superuser and note.user_id != request.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        Note.objects.delete(pk=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class APICategoryViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    required_scopes = ['categories']



class APITypeViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    permission_classes = [permissions.IsAdminUser]
    required_scopes = ['types']



class APITopicViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAdminUser]
    required_scopes = ['topics']



class APIMusicFocusViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = MusicFocus.objects.all()
    serializer_class = MusicFocusSerializer
    permission_classes = [permissions.IsAdminUser]
    required_scopes = ['musicfocus']



class APIRTRCategoryViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = RTRCategory.objects.all()
    serializer_class = RTRCategorySerializer
    permission_classes = [permissions.IsAdminUser]
    required_scopes = ['rtrcategories']


class APILanguageViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAdminUser]
    required_scopes = ['languages']


class APIHostViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = [permissions.IsAdminUser]
    required_scopes = ['hosts']


'''
class APIOwnersViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = Owners.objects.all()
    serializer_class = OwnersSerializer
    permission_classes = [permissions.IsAdminUser]
    required_scopes = ['owners']
'''