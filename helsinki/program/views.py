from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404

from helsinki.program.models import BroadcastFormat, MusicFocus, Note, Show, ShowInformation, ShowTopic, TimeSlot

from datetime import date, datetime, time, timedelta

class ShowListView(ListView):
    context_object_name = 'shows'

    def get_context_data(self, **kwargs):
        context = super(ShowListView, self).get_context_data(**kwargs)

        context['broadcastformats'] = BroadcastFormat.objects.all()
        context['musicfoci'] = MusicFocus.objects.all()
        context['showinformations'] = ShowInformation.objects.all()
        context['showtopics'] = ShowTopic.objects.all()

        return context

    def get_queryset(self):
        if 'broadcastformat' in self.request.GET:
            broadcastformat = get_object_or_404(BroadcastFormat, slug=self.request.GET['broadcastformat'])

            return Show.objects.filter(broadcastformat=broadcastformat)
        elif 'musicfocus' in self.request.GET:
            musicfocus = get_object_or_404(MusicFocus, slug=self.request.GET['musicfocus'])

            return Show.objects.filter(musicfocus=musicfocus)
        elif 'showinformation' in self.request.GET:
            showinformation = get_object_or_404(ShowInformation, slug=self.request.GET['showinformation'])

            return Show.objects.filter(showinformation=showinformation)
        elif 'showtopic' in self.request.GET:
            showtopic = get_object_or_404(ShowTopic, slug=self.request.GET['showtopic'])

            return Show.objects.filter(showtopic=showtopic)
        else:
            return Show.objects.all()

class RecommendationsView(ListView):
    context_object_name = 'recommendations'
    template_name = 'program/recommendations.html'

    def get_queryset(self):
        now = datetime.now()
        in_one_week = now + timedelta(weeks=1)

        return Note.objects.filter(status=1, timeslot__start__range=(now, in_one_week))[:10]

class TodayScheduleView(TemplateView):
    template_name = 'program/day_schedule.html'

    def get_context_data(self, **kwargs):
        context = super(TodayScheduleView, self).get_context_data(**kwargs)

        now = datetime.now()
        today = datetime.combine(date.today(), time(6, 0))
        tomorrow = datetime.combine(date.today()+timedelta(days=1), time(6, 0))

        context['day'] = today
        context['broadcastformats'] = BroadcastFormat.objects.all()
        context['recommendations'] = Note.objects.filter(status=1, timeslot__start__range=(now, tomorrow))

        if 'broadcastformat' in self.request.GET:
            broadcastformat = get_object_or_404(BroadcastFormat, slug=self.request.GET['broadcastformat'])

            context['timeslots'] = TimeSlot.objects.filter(start__range=(today, tomorrow), show__broadcastformat=broadcastformat)
        else:
            context['timeslots'] = TimeSlot.objects.filter(start__range=(today, tomorrow))

        return context

class DayScheduleView(TemplateView):
    template_name = 'program/day_schedule.html'

    def get_context_data(self, **kwargs):
        context = super(DayScheduleView, self).get_context_data(**kwargs)

        year = context['params']['year']
        month = context['params']['month']
        day = context['params']['day']

        # start the day at 6
        this_day = datetime.strptime('%s__%s__%s__06__00' % (year, month, day), '%Y__%m__%d__%H__%M')
        that_day = this_day+timedelta(days=1)

        context['day'] = this_day
        context['broadcastformats'] = BroadcastFormat.objects.all()
        context['recommendations'] = Note.objects.filter(status=1, timeslot__start__range=(this_day, that_day))

        if 'broadcastformat' in self.request.GET:
            broadcastformat = get_object_or_404(BroadcastFormat, slug=self.request.GET['broadcastformat'])

            context['timeslots'] = TimeSlot.objects.filter(start__range=(this_day, that_day), show__broadcastformat=broadcastformat)
        else:
            context['timeslots'] = TimeSlot.objects.filter(start__range=(this_day, that_day))

        return context
    
class CurrentShowView(TemplateView):
    template_name = 'program/current_box.html'

    def get_context_data(self, **kwargs):
        context = super(CurrentShowView, self).get_context_data(**kwargs)

        context['current'] = TimeSlot.objects.get_or_create_current()
        context['next'] = TimeSlot.objects.get_or_create_current().get_next_by_start()
        context['after_next'] = TimeSlot.objects.get_or_create_current().get_next_by_start().get_next_by_start()

        return context

class WeekScheduleView(TemplateView):
    template_name = 'program/week_schedule.html'

    def get_context_data(self, **kwargs):
        context = super(WeekScheduleView, self).get_context_data(**kwargs)

        year = context['params']['year']
        week = context['params']['week']

        # start the day at 6
        monday = datetime.strptime('%s__%s__1__06__00' % (year, week), '%Y__%W__%w__%H__%M')

        tuesday = monday+timedelta(days=1)
        wednesday = monday+timedelta(days=2)
        thursday = monday+timedelta(days=3)
        friday = monday+timedelta(days=4)
        saturday = monday+timedelta(days=5)
        sunday = monday+timedelta(days=6)
        next_monday = monday+timedelta(days=7)

        context['monday'] = monday
        context['tuesday'] = tuesday
        context['wednesday'] = wednesday
        context['thursday'] = thursday
        context['friday'] = friday
        context['saturday'] = saturday
        context['sunday'] = sunday
        
        context['monday_timeslots'] = TimeSlot.objects.filter(start__range=(monday, tuesday))
        context['tuesday_timeslots'] = TimeSlot.objects.filter(start__range=(tuesday, wednesday))
        context['wednesday_timeslots'] = TimeSlot.objects.filter(start__range=(wednesday, thursday))
        context['thursday_timeslots'] = TimeSlot.objects.filter(start__range=(thursday, friday))
        context['friday_timeslots'] = TimeSlot.objects.filter(start__range=(friday, saturday))
        context['saturday_timeslots'] = TimeSlot.objects.filter(start__range=(saturday, sunday))
        context['sunday_timeslots'] = TimeSlot.objects.filter(start__range=(sunday, next_monday))

        return context