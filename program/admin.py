from django.core.exceptions import ObjectDoesNotExist
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from django.conf import settings

from .models import Language, Type, MusicFocus, Category, Topic, RTRCategory, Host, Note, RRule, Schedule, Show, TimeSlot
from .forms import MusicFocusForm

from datetime import date, datetime, time, timedelta

class ActivityFilter(admin.SimpleListFilter):
    title = _("Activity")

    def lookups(self, request, model_admin):
        return (
            ('yes', _("active")),
            ('no', _("inactive"))
        )

    def queryset(self, request, queryset):
        if self.parameter_name == 'has_timeslots':  # active/inactive Schedules
            if self.value() == 'yes':
                return queryset.filter(until__gt=datetime.now()).distinct()
            if self.value() == 'no':
                return queryset.filter(until__lt=datetime.now()).distinct()

        if self.parameter_name == 'has_schedules_timeslots':  # active/inactive Shows
            if self.value() == 'yes':
                return queryset.filter(schedules__until__gt=datetime.now()).distinct()
            if self.value() == 'no':
                return queryset.filter(schedules__until__lt=datetime.now()).distinct()

        if self.parameter_name == 'has_shows_schedules_timeslots':  # active/inactive Hosts
            if self.value() == 'yes':
                return queryset.filter(shows__schedules__until__gt=datetime.now()).distinct()
            if self.value() == 'no':
                return queryset.filter(shows__schedules__until__lt=datetime.now()).distinct()


class ActiveSchedulesFilter(ActivityFilter):
    parameter_name = 'has_timeslots'


class ActiveShowsFilter(ActivityFilter):
    parameter_name = 'has_schedules_timeslots'


class ActiveHostsFilter(ActivityFilter):
    parameter_name = 'has_shows_schedules_timeslots'


class TypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'admin_color', 'enabled')
    prepopulated_fields = {'slug': ('type',)}


class MusicFocusAdmin(admin.ModelAdmin):
    form = MusicFocusForm
    list_display = ('focus', 'abbrev', 'admin_buttons')
    prepopulated_fields = {'slug': ('focus',)}


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'abbrev', 'admin_buttons')
    prepopulated_fields = {'slug': ('category',)}


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)


class TopicAdmin(admin.ModelAdmin):
    list_display = ('topic', 'abbrev', 'admin_buttons')
    prepopulated_fields = {'slug': ('topic',)}


class RTRCategoryAdmin(admin.ModelAdmin):
    list_display = ('rtrcategory', 'abbrev', )
    prepopulated_fields = {'slug': ('rtrcategory',)}


class HostAdmin(admin.ModelAdmin):
    list_display = ('name','email',)
    list_filter = (ActiveHostsFilter, 'is_always_visible',)


class NoteAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('title', 'show', 'start', 'status', 'user')
    fields = (( 'show', 'timeslot'), 'title', 'slug', 'summary', 'content', 'image', 'status', 'cba_id')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status',)
    ordering = ('timeslot',)
    save_as = True

    class Media:
        js = [ settings.MEDIA_URL + 'js/calendar/lib/moment.min.js',
               settings.MEDIA_URL + 'js/note_change.js', ]

    def get_queryset(self, request):
        if request.user.is_superuser:
            # Superusers see notes of all shows
            shows = Show.objects.all()
        else:
            # Users only see notes of shows they own
            shows = request.user.shows.all()

        return super(NoteAdmin, self).get_queryset(request).filter(show__in=shows)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        four_weeks_ago = datetime.now() - timedelta(weeks=4)
        in_twelve_weeks = datetime.now() + timedelta(weeks=12)

        if db_field.name == 'timeslot':
            # Adding/Editing a note: load timeslots of the user's shows into the dropdown

            # TODO: Don't show any timeslot in the select by default.
            #       User should first choose show, then timeslots are loaded into the select via ajax.
            #
            # How to do this while not constraining the queryset?
            # Saving won't be possible otherwise, if queryset doesn't contain the selectable elements beforehand
            #kwargs['queryset'] = TimeSlot.objects.filter(show=-1)

            # Superusers see every timeslot for every show
            if request.user.is_superuser:
                kwargs['queryset'] = TimeSlot.objects.filter(start__gt=four_weeks_ago,
                                                             start__lt=in_twelve_weeks) # note__isnull=True
            # Users see timeslots of shows they own
            else:
                kwargs['queryset'] = TimeSlot.objects.filter(show__in=request.user.shows.all(), start__gt=four_weeks_ago,
                                                             start__lt=in_twelve_weeks) # note__isnull=True

        if db_field.name == 'show':
            # Adding/Editing a note: load user's shows into the dropdown

            # Superusers see all shows
            if not request.user.is_superuser:
                kwargs['queryset'] = Show.objects.filter(pk__in=request.user.shows.all())

        return super(NoteAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):

        # Save the creator when adding a note
        if not change:
            obj.user = request.user

        # Try to get direct audio URL from CBA
        obj.audio_url = Note.get_audio_url(obj.cba_id)

        obj.save()


class TimeSlotInline(admin.TabularInline):
    model = TimeSlot
    ordering = ('-end',)

class TimeSlotAdmin(admin.ModelAdmin):
    model = TimeSlot


class ScheduleAdmin(admin.ModelAdmin):
    actions = ('renew',)
    inlines = (TimeSlotInline,)
    fields = (('rrule', 'byweekday'), ('dstart', 'tstart', 'tend'), 'until', 'is_repetition', 'automation_id', 'fallback_id')
    list_display = ('get_show_name', 'byweekday', 'rrule', 'tstart', 'tend', 'until')
    list_filter = (ActiveSchedulesFilter, 'byweekday', 'rrule', 'is_repetition')
    ordering = ('byweekday', 'dstart')
    save_on_top = True
    search_fields = ('show__name',)

    def renew(self, request, queryset):
        next_year = date.today().year + 1
        until = date(next_year, 12, 31)
        renewed = queryset.update(until=until)
        if renewed == 1:
            message = _("1 schedule was renewed until %s") % until
        else:
            message = _("%s schedule were renewed until %s") % (renewed, until)
        self.message_user(request, message)
    renew.short_description = _("Renew selected schedules")

    def get_show_name(self, obj):
        return obj.show.name
    get_show_name.admin_order_field = 'show'
    get_show_name.short_description = "Show"


class ScheduleInline(admin.TabularInline):
    model = Schedule
    ordering = ('pk', '-until', 'byweekday')


class ShowAdmin(admin.ModelAdmin):
    filter_horizontal = ('hosts', 'owners', 'musicfocus', 'category', 'topic', 'language')
    inlines = (ScheduleInline,)
    list_display = ('name', 'short_description')
    list_filter = (ActiveShowsFilter, 'type', 'category', 'topic', 'musicfocus', 'rtrcategory', 'language')
    ordering = ('slug',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'short_description', 'description')
    fields = (
        'predecessor', 'type', 'name', 'slug', 'image', 'logo', 'short_description', 'description',
        'email', 'website', 'hosts', 'owners', 'language', 'category', 'rtrcategory', 'topic',
        'musicfocus', 'fallback_id', 'cba_series_id',
    )


    class Media:
        js = [ settings.MEDIA_URL + 'js/calendar/lib/moment.min.js',
               settings.MEDIA_URL + 'js/show_change.js', ]

        css = { 'all': ('/program/styles.css',) }


    def get_queryset(self, request):
        if request.user.is_superuser:
            # Superusers see all shows
            shows = Show.objects.all()
        else:
            # Users only see shows they own
            shows = request.user.shows.all()

        return super(ShowAdmin, self).get_queryset(request).filter(pk__in=shows)


    def get_readonly_fields(self, request, obj=None):
        '''Limit field access for common users'''
        if not request.user.is_superuser:
            return ('predecessor', 'type', 'hosts', 'owners', 'language', 'category', 'topic', 'musicfocus', 'rtrcategory')
        return list()


    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        try:
            show_id = int(request.get_full_path().split('/')[-2])
        except ValueError:
            show_id = None

        if db_field.name == 'predecessor' and show_id:
            kwargs['queryset'] = Show.objects.exclude(pk=show_id)

        return super(ShowAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


    def save_formset(self, request, form, formset, change):
        """
        Is called after the "save show"-form or collision-form were submitted

        Saves the show after first submit

        If any changes in schedules happened
          * added/changed schedules are used to generate new timeslots and
            matched against existing ones, which will be displayed in the collision form

        If a collision form was submitted
          * save the current schedule
          * delete/create timeslots and relink notes after confirmation

        Each step passes on to response_add or response_change which will
          * either display the collision form for the next step
          * or redirect to the original show-form if the resolving process has been finished
            (= if either max_steps was surpassed or end_reached was True)
        """
        self.end_reached = False

        schedule_instances = formset.save(commit=False)

        # If there are no schedules to save, do nothing
        if schedule_instances:
            show_id = schedule_instances[0].show.id
        else:
            self.end_reached = True

        schedule = []
        timeslots = []

        max_steps = int(len(schedule_instances)) if len(schedule_instances) > 0 else 1
        step = 1

        if request.POST.get('step') == None:
            # First save-show submit

            # Generate thumbnails
            if form.instance.image.name and settings.THUMBNAIL_SIZES:
                for size in settings.THUMBNAIL_SIZES:
                    thumbnail = form.instance.image.crop[size].name

            # Save show data only
            form.save();

            # Delete schedules (as well as related timeslots and notes) if flagged as such
            for obj in formset.deleted_objects:
                obj.delete()

            # If nothing else changed, do nothing and redirect to show-form
            if not formset.changed_objects and not formset.new_objects:
                self.end_reached = True

        else:
            # If a collision form was submitted

            step = int(request.POST.get('step'))

            if request.POST.get('num_inputs') != None and int(request.POST.get('num_inputs')) > 0:
                print("Resolving conflicts...")

                '''Declare and retrieve variables'''

                # Either datetimes as string (e.g. '2017-01-01 00:00:00 - 2017-01-01 01:00:00') to create
                # or ints of colliding timeslots to keep otherwise
                resolved_timeslots = []

                # IDs of colliding timeslots found in the db. If there's no corresponding collision to the
                # same index in create_timeslot, value will be None
                collisions = []

                # Datetimes as string (e.g. '2017-01-01 00:00:00 - 2017-01-01 01:00:00') for timeslots to create
                create_timeslots = []

                # IDs of timeslots to delete
                delete_timeslots = set()

                # Number of timeslots to be generated
                num_inputs = int(request.POST.get('num_inputs'))

                # Numbers of notes to relink for existing timeslots and newly created ones
                # each of them relating to one of these POST vars:
                #   POST.ntids[idx][id] and POST.ntids[idx][note_id] contain ids of existing timeslots and note_ids to link, while
                #   POST.ntind[idx][id] and POST.ntind[idx][note_id] contain indices of corresponding elements in create_timeslots
                #     and note_ids which will be linked after they're created and thus split into two lists beforehand
                num_ntids = int(request.POST.get('num_ntids'))
                num_ntind = int(request.POST.get('num_ntind'))

                # Retrieve POST vars of current schedule
                schedule_id = int(request.POST.get('ps_save_id')) if request.POST.get('ps_save_id') != 'None' else None
                rrule = RRule.objects.get(pk=int(request.POST.get('ps_save_rrule_id')))
                show = Show.objects.get(pk=show_id)
                byweekday = int(request.POST.get('ps_save_byweekday'))
                tstart = datetime.strptime(request.POST.get('ps_save_tstart'), '%H:%M').time()
                tend = datetime.strptime(request.POST.get('ps_save_tend'), '%H:%M').time()
                dstart = datetime.strptime(request.POST.get('ps_save_dstart'), '%Y-%m-%d').date()
                if dstart < datetime.today().date(): # Create or delete upcoming timeslots only
                    dstart = datetime.today().date()
                until = datetime.strptime(request.POST.get('ps_save_until'), '%Y-%m-%d').date()
                is_repetition = request.POST.get('ps_save_is_repetition')
                automation_id = int(request.POST.get('ps_save_automation_id')) if request.POST.get('ps_save_automation_id') != 'None' else 0
                fallback_id = int(request.POST.get('fallback_id')) if request.POST.get('ps_save_fallback_id') != 'None' else 0

                # Put timeslot POST vars into lists with same indices
                for i in range(num_inputs):
                    resolved_ts = request.POST.get('resolved_timeslots[' + str(i) + ']')
                    if resolved_ts != None:
                        resolved_timeslots.append( resolved_ts )
                        create_timeslots.append( request.POST.get('create_timeslots[' + str(i) + ']') ) # May contain None
                        collisions.append( request.POST.get('collisions[' + str(i) + ']') ) # May contain None
                    else:
                        num_inputs -= 1


                '''Prepare resolved timeslots'''

                # Separate timeslots to delete from those to create
                keep_collisions = []
                for x in range(num_inputs):
                    if resolved_timeslots[x] == None or resolved_timeslots[x].isdigit():
                        # If it's a digit, keep the existing timeslot by preventing the new one from being created
                        create_timeslots[x] = None
                        keep_collisions.append(int(collisions[x]))
                    else:
                        # Otherwise collect the timeslot ids to be deleted later
                        if len(collisions[x]) > 0:
                            delete_timeslots.add(int(collisions[x]))

                # Collect IDs of upcoming timeslots of the same schedule to delete except those in keep_collision
                if schedule_id != None:
                    for ts in TimeSlot.objects.filter(start__gte=dstart,end__lte=until,schedule_id=schedule_id).exclude(pk__in=keep_collisions).values_list('id', flat=True):
                        delete_timeslots.add(ts)


                '''Save schedule'''

                new_schedule = Schedule(pk=schedule_id,
                                              rrule=rrule,
                                              byweekday=byweekday,
                                              show=show,
                                              dstart=dstart,
                                              tstart=tstart,
                                              tend=tend,
                                              until=until,
                                              is_repetition=is_repetition,
                                              automation_id=automation_id,
                                              fallback_id=fallback_id)

                # Only save schedule if any timeslots changed
                if len(resolved_timeslots) > 0:
                    new_schedule.save()


                '''Relink notes to existing timeslots and prepare those to be linked'''

                # Relink notes with existing timeslot ids
                for i in range(num_ntids):
                    try:
                        note = Note.objects.get(pk=int(request.POST.get('ntids[' +  str(i) + '][note_id]')))
                        note.timeslot_id = int(request.POST.get('ntids[' + str(i) + '][id]'))
                        note.save(update_fields=["timeslot_id"])
                        print("Rewrote note " + str(note.id) + "...to timeslot_id " + str(note.timeslot_id))
                    except ObjectDoesNotExist:
                        pass

                # Put list indices of yet to be created timeslots and note_ids in corresponding lists to relink them during creation
                note_indices = []
                note_ids = []
                for i in range(num_ntind):
                    note_indices.append( int(request.POST.get('ntind[' + str(i) + '][id]')) )
                    note_ids.append( int(request.POST.get('ntind[' +  str(i) + '][note_id]')) )


                '''Database changes for resolved timeslots and relinked notes for newly created'''

                for idx, ts in enumerate(create_timeslots):
                    if ts != None:
                        start_end = ts.split(' - ')
                        # Only create upcoming timeslots
                        if datetime.strptime(start_end[0], "%Y-%m-%d %H:%M:%S") > datetime.today():
                            timeslot_created = TimeSlot.objects.create(schedule=new_schedule, is_repetition=new_schedule.is_repetition, start=start_end[0], end=start_end[1])

                            # Link a note to the new timeslot
                            if idx in note_indices:
                                note_idx = note_indices.index( idx ) # Get the note_id's index...
                                note_id = note_ids[note_idx] # ...which contains the note_id to relate to

                                try:
                                    note = Note.objects.get(pk=note_id)
                                    note.timeslot_id = timeslot_created.id
                                    note.save(update_fields=["timeslot_id"])
                                    print("Timeslot " + str(timeslot_created.id) + " linked to note " + str(note_id))
                                except ObjectDoesNotExist:
                                    pass

                # Finally delete discarded timeslots
                for timeslot_id in delete_timeslots:
                    TimeSlot.objects.filter(pk=timeslot_id).delete()


        if step > max_steps:
            self.end_reached = True


        '''
        Everything below here is called when a new collision is loaded before being handed over to the client
        '''

        # Generate timeslots from current schedule
        k = 1
        for instance in schedule_instances:
            if isinstance(instance, Schedule):
                if k == step:
                    timeslots = Schedule.generate_timeslots(instance)
                    schedule = instance
                    break
                k += 1

        # Get collisions for timeslots
        collisions = Schedule.get_collisions(timeslots)

        # Get notes of colliding timeslots
        notes = []
        for id in collisions:
            try:
                notes.append( Note.objects.get(timeslot_id=id) )
            except ObjectDoesNotExist:
                pass

        self.schedule = schedule
        self.timeslots = timeslots
        self.collisions = collisions
        self.num_collisions = len([ s for s in self.collisions if s != 'None']) # Number of real collisions displayed to the user
        self.notes = notes
        self.showform = form
        self.schedulesform = formset
        self.step = step + 1 # Becomes upcoming step
        self.max_steps = max_steps

        # Pass it on to response_add() or response_change()
        return self


    def response_add(self, request, obj):
        return ShowAdmin.respond(self, request, obj)


    def response_change(self, request, obj):
        return ShowAdmin.respond(self, request, obj)


    def respond(self, request, obj):
        """
        Redirects to the show-change-form if no schedules changed or resolving has been finished (or any other form validation error occured)
        Displays the collision form for the current schedule otherwise
        """

        # Never check for collisions if not superuser
        # Common users can't edit the formset, so save_formset() will never be called thus end_reached wasn't set yet
        if not request.user.is_superuser:
           self.end_reached = True

        if self.end_reached:
            return super(ShowAdmin, self).response_change(request, obj)

        timeslots_to_collisions = list(zip(self.timeslots, self.collisions))

        return render(request, 'collisions.html', {'self' : self, 'obj': obj, 'request': request,
                                                   'timeslots': self.timeslots,
                                                   'collisions': self.collisions,
                                                   'schedule': self.schedule,
                                                   'timeslots_to_collisions': timeslots_to_collisions,
                                                   'schedulesform': self.schedulesform,
                                                   'showform': self.showform,
                                                   'num_inputs': len(self.timeslots),
                                                   'step': self.step,
                                                   'max_steps': self.max_steps,
                                                   'now': datetime.now(),
                                                   'num_collisions': self.num_collisions})


admin.site.register(Language, LanguageAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(MusicFocus, MusicFocusAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(RTRCategory, RTRCategoryAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(Note, NoteAdmin)
#admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(Show, ShowAdmin)