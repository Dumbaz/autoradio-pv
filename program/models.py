from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError, MultipleObjectsReturned
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _
from versatileimagefield.fields import VersatileImageField, PPOIField
from django.conf import settings
import hashlib

from tinymce import models as tinymce_models

from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule

from .utils import get_automation_id_choices

from pv.settings import SECRET_KEY, AUTO_SET_UNTIL_DATE_TO_END_OF_YEAR, AUTO_SET_UNTIL_DATE_TO_DAYS_IN_FUTURE


class Type(models.Model):
    type = models.CharField(_("Type"), max_length=32)
    slug = models.SlugField(_("Slug"), max_length=32, unique=True)
    is_active = models.BooleanField(_("Is active?"), default=True)
    color = models.CharField(_("Color"), max_length=7, default='#ffffff')
    text_color = models.CharField(_("Text color"), max_length=7, default='#000000')

    class Meta:
        ordering = ('type',)
        verbose_name = _("Type")
        verbose_name_plural = _("Types")

    def admin_color(self):
        return '<span style="background-color: %s; color: %s; padding: 0.2em">%s/%s</span>' % (
            self.color, self.text_color, self.color, self.text_color)

    admin_color.short_description = _("Color")
    admin_color.allow_tags = True

    def __str__(self):
        return '%s' % self.type


class Category(models.Model):
    category = models.CharField(_("Category"), max_length=32)
    abbrev = models.CharField(_("Abbreviation"), max_length=4, unique=True)
    slug = models.SlugField(_("Slug"), max_length=32, unique=True)
    is_active = models.BooleanField(_("Is active?"), default=True)
    color = models.TextField(_("Color"), max_length=7, blank=True)
    description = models.TextField(_("Description"), blank=True)
    button = models.ImageField(_("Button image"), blank=True, null=True, upload_to='buttons')
    button_hover = models.ImageField(_("Button image (hover)"), blank=True, null=True, upload_to='buttons')
    big_button = models.ImageField(_("Big button image"), blank=True, null=True, upload_to='buttons')

    class Meta:
        ordering = ('category',)
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def admin_buttons(self):
        buttons = []
        if self.button:
            buttons.append('<img src="%s" />' % self.button.url)
        else:
            buttons.append('x')

        if self.button_hover:
            buttons.append('<img src="%s" />' % self.button_hover.url)
        else:
            buttons.append('x')

        if self.big_button:
            buttons.append('<img src="%s" />' % self.big_button.url)
        else:
            buttons.append('x')

        return ' '.join(buttons)

    admin_buttons.short_description = _("Buttons")
    admin_buttons.allow_tags = True

    def button_url(self):
        if self.button:
            return self.button.url
        else:
            return '/site_media/buttons/default-11.png'

    def button_hover_url(self):
        if self.button_hover:
            return self.button_hover.url
        else:
            return '/site_media/buttons/default-11.png'

    def big_button_url(self):
        if self.big_button:
            return self.big_button.url
        else:
            return '/site_media/buttons/default-17.png'

    def __str__(self):
        return '%s' % self.category


class Topic(models.Model):
    topic = models.CharField(_("Topic"), max_length=32)
    abbrev = models.CharField(_("Abbreviation"), max_length=4, unique=True)
    slug = models.SlugField(_("Slug"), max_length=32, unique=True)
    is_active = models.BooleanField(_("Is active?"), default=True)
    button = models.ImageField(_("Button image"), blank=True, null=True, upload_to='buttons')
    button_hover = models.ImageField(_("Button image (hover)"), blank=True, null=True, upload_to='buttons')
    big_button = models.ImageField(_("Big button image"), blank=True, null=True, upload_to='buttons')

    class Meta:
        ordering = ('topic',)
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")

    def admin_buttons(self):
        buttons = []
        if self.button:
            buttons.append('<img src="%s" />' % self.button.url)
        else:
            buttons.append('x')

        if self.button_hover:
            buttons.append('<img src="%s" />' % self.button_hover.url)
        else:
            buttons.append('x')

        if self.big_button:
            buttons.append('<img src="%s" />' % self.big_button.url)
        else:
            buttons.append('x')

        return ' '.join(buttons)

    admin_buttons.short_description = _("Buttons")
    admin_buttons.allow_tags = True

    def button_url(self):
        if self.button:
            return self.button.url
        else:
            return '/site_media/buttons/default-11.png'

    def button_hover_url(self):
        if self.button_hover:
            return self.button_hover.url
        else:
            return '/site_media/buttons/default-11.png'

    def big_button_url(self):
        if self.big_button:
            return self.big_button.url
        else:
            return '/site_media/buttons/default-17.png'

    def __str__(self):
        return '%s' % self.topic


class MusicFocus(models.Model):
    focus = models.CharField(_("Focus"), max_length=32)
    abbrev = models.CharField(_("Abbreviation"), max_length=4, unique=True)
    slug = models.SlugField(_("Slug"), max_length=32, unique=True)
    is_active = models.BooleanField(_("Is active?"), default=True)
    button = models.ImageField(_("Button image"), blank=True, null=True, upload_to='buttons')
    button_hover = models.ImageField(_("Button image (hover)"), blank=True, null=True, upload_to='buttons')
    big_button = models.ImageField(_("Big button image"), blank=True, null=True, upload_to='buttons')

    class Meta:
        ordering = ('focus',)
        verbose_name = _("Music focus")
        verbose_name_plural = _("Music focus")

    def admin_buttons(self):
        buttons = []
        if self.button:
            buttons.append('<img src="%s" />' % self.button.url)
        else:
            buttons.append('x')

        if self.button_hover:
            buttons.append('<img src="%s" />' % self.button_hover.url)
        else:
            buttons.append('x')

        if self.big_button:
            buttons.append('<img src="%s" />' % self.big_button.url)
        else:
            buttons.append('x')

        return ' '.join(buttons)

    admin_buttons.short_description = _("Buttons")
    admin_buttons.allow_tags = True

    def button_url(self):
        if self.button:
            return self.button.url
        else:
            return '/site_media/buttons/default-11.png'

    def button_hover_url(self):
        if self.button_hover:
            return self.button_hover.url
        else:
            return '/site_media/buttons/default-11.png'

    def big_button_url(self):
        if self.big_button:
            return self.big_button.url
        else:
            return '/site_media/buttons/default-17.png'

    def __str__(self):
        return '%s' % self.focus


class RTRCategory(models.Model):
    rtrcategory = models.CharField(_("RTR Category"), max_length=32)
    abbrev = models.CharField(_("Abbreviation"), max_length=4, unique=True)
    slug = models.SlugField(_("Slug"), max_length=32, unique=True)
    is_active = models.BooleanField(_("Is active?"), default=True)

    class Meta:
        ordering = ('rtrcategory',)
        verbose_name = _("RTR Category")
        verbose_name_plural = _("RTR Categories")

    def __str__(self):
        return '%s' % self.rtrcategory


class Language(models.Model):
    name = models.CharField(_("Language"), max_length=32)
    is_active = models.BooleanField(_("Is active?"), default=True)

    class Meta:
        ordering = ('language',)
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __str__(self):
        return '%s' % self.name


class Host(models.Model):
    name = models.CharField(_("Name"), max_length=128)
    is_active = models.BooleanField(_("Is active?"), default=True)
    email = models.EmailField(_("E-Mail"), blank=True)
    website = models.URLField(_("Website"), blank=True, help_text=_("URL to your personal website."))
    biography = tinymce_models.HTMLField(_("Biography"), blank=True, null=True, help_text=_("Describe yourself and your fields of interest in a few sentences."))
    googleplus_url = models.URLField(_("Google+ URL"), blank=True, help_text=_("URL to your Google+ profile."))
    facebook_url = models.URLField(_("Facebook URL"), blank=True, help_text=_("URL to your Facebook profile."))
    twitter_url = models.URLField(_("Twitter URL"), blank=True, help_text=_("URL to your Twitter profile."))
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True, help_text=_("URL to your LinkedIn profile."))
    youtube_url = models.URLField(_("Youtube URL"), blank=True, help_text=_("URL to your Youtube channel."))
    dorftv_url = models.URLField(_("DorfTV URL"), blank=True, help_text=_("URL to your dorfTV channel."))
    cba_url = models.URLField(_("CBA URL"), blank=True, help_text=_("URL to your CBA profile."))
    ppoi = PPOIField('Image PPOI')
    height = models.PositiveIntegerField('Image Height', blank=True, null=True, editable=False)
    width = models.PositiveIntegerField('Image Width', blank=True, null=True,editable=False)
    image = VersatileImageField(_("Profile picture"), blank=True, null=True, upload_to='host_images', width_field='width', height_field='height', ppoi_field='ppoi', help_text=_("Upload a picture of yourself. Images are automatically cropped around the 'Primary Point of Interest'. Click in the image to change it and press Save."))

    class Meta:
        ordering = ('name',)
        verbose_name = _("Host")
        verbose_name_plural = _("Hosts")

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('host-detail', args=[str(self.id)])

    def active_shows(self):
        return self.shows.filter(schedules__until__gt=datetime.today())

    def is_editable(self, host_id):
        """
        Whether the given host is assigned to a show the current user owns
        @return boolean
        """
        if self.request.user.is_superuser:
            return True

        host_ids = Host.objects.filter(shows__in=self.request.user.shows.all()).distinct().values_list('id', flat=True)
        return int(host_id) in host_ids

    def save(self, *args, **kwargs):
        super(Host, self).save(*args, **kwargs)

        # Generate thumbnails
        if self.image.name and settings.THUMBNAIL_SIZES:
            for size in settings.THUMBNAIL_SIZES:
                thumbnail = self.image.crop[size].name


class Show(models.Model):
    predecessor = models.ForeignKey('self', blank=True, null=True, related_name='successors', verbose_name=_("Predecessor"))
    hosts = models.ManyToManyField(Host, blank=True, related_name='shows', verbose_name=_("Hosts"))
    owners = models.ManyToManyField(User, blank=True, related_name='shows', verbose_name=_("Owners"))
    language = models.ManyToManyField(Language, blank=True, related_name='language', verbose_name=_("Language"))
    type = models.ForeignKey(Type, related_name='shows', verbose_name=_("Type"))
    category = models.ManyToManyField(Category, blank=True, related_name='shows', verbose_name=_("Category"))
    rtrcategory = models.ForeignKey(RTRCategory, related_name='shows', verbose_name=_("RTR Category"))
    topic = models.ManyToManyField(Topic, blank=True, related_name='shows', verbose_name=_("Topic"))
    musicfocus = models.ManyToManyField(MusicFocus, blank=True, related_name='shows', verbose_name=_("Music focus"))
    name = models.CharField(_("Name"), max_length=255, help_text=_("The show's name. Avoid a subtitle."))
    slug = models.CharField(_("Slug"), max_length=255, unique=True, help_text=_("A simple to read URL for your show"))
    ppoi = PPOIField('Image PPOI')
    height = models.PositiveIntegerField('Image Height', blank=True, null=True, editable=False)
    width = models.PositiveIntegerField('Image Width', blank=True, null=True,editable=False)
    image = VersatileImageField(_("Image"), blank=True, null=True, upload_to='show_images', width_field='width', height_field='height', ppoi_field='ppoi', help_text=_("Upload an image to your show. Images are automatically cropped around the 'Primary Point of Interest'. Click in the image to change it and press Save."))
    logo = models.ImageField(_("Logo"), blank=True, null=True, upload_to='show_images')
    short_description = models.TextField(_("Short description"), help_text=_("Describe your show in some sentences. Avoid technical data like airing times and contact information. They will be added automatically."))
    description = tinymce_models.HTMLField(_("Description"), blank=True, null=True, help_text=_("Describe your show in detail."))
    email = models.EmailField(_("E-Mail"), blank=True, null=True, help_text=_("The main contact email address for your show."))
    website = models.URLField(_("Website"), blank=True, null=True, help_text=_("Is there a website to your show? Type in its URL."))
    cba_series_id = models.IntegerField(_("CBA Series ID"), blank=True, null=True, help_text=_("Link your show to a CBA series by giving its ID. This will enable CBA upload and will automatically link your show to your CBA archive. Find out your ID under https://cba.fro.at/series"))
    fallback_id = models.IntegerField(_("Fallback ID"), blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('slug',)
        verbose_name = _("Show")
        verbose_name_plural = _("Shows")

    def __str__(self):
        if self.id == None:
            return '%s' % (self.name)

        return '%04d | %s' % (self.id, self.name)

    def get_absolute_url(self):
        return reverse('show-detail', args=[self.slug])

    # Called by show templates
    def active_schedules(self):
        return self.schedules.filter(until__gt=date.today())

    def is_editable(self, show_id):
        """
        Whether the current user is owner of the given show
        @return boolean
        """
        if self.request.user.is_superuser:
            return True

        show_ids = self.request.user.shows.all().values_list('id', flat=True)
        return int(show_id) in show_ids


class RRule(models.Model):

    FREQ_CHOICES = (
        (1, _("Monthly")),
        (2, _("Weekly")),
        (3, _("Daily")),
    )

    BYSETPOS_CHOICES = (
        (1, _("First")),
        (2, _("Second")),
        (3, _("Third")),
        (4, _("Fourth")),
        (5, _("Fifth")),
        (-1, _("Last")),
    )
    name = models.CharField(_("Name"), max_length=32, unique=True)
    freq = models.IntegerField(_("Frequency"), choices=FREQ_CHOICES)
    interval = models.IntegerField(_("Interval"), default=1)
    bysetpos = models.IntegerField(_("Set position"), blank=True,
                                   choices=BYSETPOS_CHOICES, null=True)
    count = models.IntegerField(_("Count"), blank=True, null=True)

    class Meta:
        ordering = ('pk',)
        verbose_name = _("Recurrence rule")
        verbose_name_plural = _("Recurrence rules")

    def __str__(self):
        return '%s' % self.name


class Schedule(models.Model):
    BYWEEKDAY_CHOICES = (
        (0, _("Monday")),
        (1, _("Tuesday")),
        (2, _("Wednesday")),
        (3, _("Thursday")),
        (4, _("Friday")),
        (5, _("Saturday")),
        (6, _("Sunday")),
    )

    rrule = models.ForeignKey(RRule, related_name='schedules', verbose_name=_("Recurrence rule"))
    byweekday = models.IntegerField(_("Weekday"), choices=BYWEEKDAY_CHOICES)
    show = models.ForeignKey(Show, related_name='schedules', verbose_name=_("Show"))
    dstart = models.DateField(_("First date"))
    tstart = models.TimeField(_("Start time"))
    tend = models.TimeField(_("End time"))
    until = models.DateField(_("Last date"))
    is_repetition = models.BooleanField(_("Is repetition"), default=False)
    fallback_id = models.IntegerField(_("Fallback ID"), blank=True, null=True)
    automation_id = models.IntegerField(_("Automation ID"), blank=True, null=True, choices=get_automation_id_choices()) # Deprecated
    created = models.DateTimeField(auto_now_add=True, editable=False, null=True) #-> both see https://stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add
    last_updated = models.DateTimeField(auto_now=True, editable=False, null=True)

    class Meta:
        ordering = ('dstart', 'tstart')
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")

    def __str__(self):
        weekday = self.BYWEEKDAY_CHOICES[self.byweekday][1]
        tend = self.tend.strftime('%H:%M')
        dstart = self.dstart.strftime('%d. %b %Y')
        tstart = self.tstart.strftime('%H:%M')

        if self.rrule.freq == 0:
            return '%s %s, %s - %s' % (self.rrule, dstart, tstart, tend)
        if self.rrule.freq == 3:
            return '%s, %s - %s' % (self.rrule, tstart, tend)
        else:
            return '%s, %s, %s - %s' % (weekday, self.rrule, tstart, tend)

    def instantiate_upcoming(sdl, show_pk, pk=None):
        """Returns an upcoming schedule instance for conflict resolution"""

        pk = int(show_pk) if pk != None else None
        rrule = RRule.objects.get(pk=int(sdl['rrule']))
        show = Show.objects.get(pk=int(show_pk))

        is_repetition = True if 'is_repetition' in sdl and sdl['is_repetition'] == 'true' else False
        fallback_id = int(sdl['fallback_id']) if sdl['fallback_id'] else None
        automation_id = int(sdl['automation_id']) if sdl['automation_id'] else None

        dstart = datetime.strptime(str(sdl['dstart']), '%Y-%m-%d').date()
        if dstart < datetime.today().date(): # Schedule mustn't start in the past
            dstart = datetime.today().date()

        tstart = sdl['tstart'] + ':00' if len(str(sdl['tstart'])) == 5 else sdl['tstart']
        tend = sdl['tend'] + ':00' if len(str(sdl['tend'])) == 5 else sdl['tend']

        tstart = datetime.strptime(str(tstart), '%H:%M:%S').time()
        tend = datetime.strptime(str(tend), '%H:%M:%S').time()

        if sdl['until']:
            until = datetime.strptime(str(sdl['until']), '%Y-%m-%d').date()
        else:
            # If no until date was set
            # Set it to the end of the year
            # Or add x days
            if AUTO_SET_UNTIL_DATE_TO_END_OF_YEAR:
                now = datetime.now()
                until = datetime.strptime(str(now.year) + '-12-31', '%Y-%m-%d').date()
            else:
                until = dstart + timedelta(days=+AUTO_SET_UNTIL_DATE_TO_DAYS_IN_FUTURE)

        schedule = Schedule(pk=pk, byweekday=sdl['byweekday'], rrule=rrule,
                            dstart=dstart, tstart=tstart, tend=tend,
                            until=until, is_repetition=is_repetition,
                            fallback_id=fallback_id, show=show)

        return schedule


    def generate_timeslots(schedule):
        """
        Returns a list of timeslot objects based on a schedule and its rrule
        Returns past timeslots as well, starting from dstart (not today)
        """

        byweekno = None
        byweekno_end = None
        byweekday_end = int(schedule.byweekday)
        starts = []
        ends = []
        timeslots = []

        # Handle ending weekday for timeslots over midnight
        if schedule.tend < schedule.tstart:
            if schedule.byweekday < 6:
                byweekday_end = int(schedule.byweekday + 1)
            else:
                byweekday_end = 0

        # Handle ending dates for timeslots over midnight
        if schedule.tend < schedule.tstart:
            dend = schedule.dstart + timedelta(days=+1)
        else:
            dend = schedule.dstart

        if schedule.rrule.freq == 0: # Ignore weekdays for one-time timeslots
            byweekday_start = None
            byweekday_end = None
        elif schedule.rrule.freq == 3 and schedule.rrule.pk == 2: # Daily timeslots
            byweekday_start = (0, 1, 2, 3, 4, 5, 6)
            byweekday_end = (0, 1, 2, 3, 4, 5, 6)
        elif schedule.rrule.freq == 3 and schedule.rrule.pk == 3: # Business days MO - FR/SA
            byweekday_start = (0, 1, 2, 3, 4)
            if schedule.tend < schedule.tstart:
                # End days for over midnight
                byweekday_end = (1, 2, 3, 4, 5)
            else:
                byweekday_end = (0, 1, 2, 3, 4)
        elif schedule.rrule.freq == 2 and schedule.rrule.pk == 7: # Even calendar weeks
            byweekday_start = int(schedule.byweekday)
            byweekno = list(range(2, 54, 2))
            # Reverse ending weeks if from Sun - Mon
            if byweekday_start == 6 and byweekday_end == 0:
                byweekno_end = list(range(1, 54, 2))
            else:
                byweekno_end = byweekno
        elif schedule.rrule.freq == 2 and schedule.rrule.pk == 8: # Odd calendar weeks
            byweekday_start = int(schedule.byweekday)
            byweekno = list(range(1, 54, 2))
            # Reverse ending weeks if from Sun - Mon
            if byweekday_start == 6 and byweekday_end == 0:
                byweekno_end = list(range(2, 54, 2))
            else:
                byweekno_end = byweekno
        else:
            byweekday_start = int(schedule.byweekday)

        if schedule.rrule.freq == 0:
            starts.append(datetime.combine(schedule.dstart, schedule.tstart))
            ends.append(datetime.combine(dend, schedule.tend))
        else:

            starts = list(rrule(freq=schedule.rrule.freq,
                            dtstart=datetime.combine(schedule.dstart, schedule.tstart),
                            interval=schedule.rrule.interval,
                            until=schedule.until + relativedelta(days=+1),
                            bysetpos=schedule.rrule.bysetpos,
                            byweekday=byweekday_start,
                            byweekno=byweekno))

            ends = list(rrule(freq=schedule.rrule.freq,
                          dtstart=datetime.combine(dend, schedule.tend),
                          interval=schedule.rrule.interval,
                          until=schedule.until + relativedelta(days=+1),
                          bysetpos=schedule.rrule.bysetpos,
                          byweekday=byweekday_end,
                          byweekno=byweekno_end))

        for k in range(min(len(starts), len(ends))):
            timeslots.append(TimeSlot(schedule=schedule, start=starts[k], end=ends[k]).generate())

        return timeslots


    def get_collisions(timeslots):
        """
        Tests a list of timeslot objects for colliding timeslots in the database
        Returns a list of collisions, containing colliding timeslot IDs or None
        Keeps indices from input list for later comparison
        """

        collisions = []

        for ts in timeslots:

            collision = TimeSlot.objects.filter(
                           ( Q(start__lt=ts.end) & Q(end__gte=ts.end) ) |
                           ( Q(end__gt=ts.start) & Q(end__lte=ts.end) ) |
                           ( Q(start__gte=ts.start) & Q(end__lte=ts.end) ) |
                           ( Q(start__lte=ts.start) & Q(end__gte=ts.end) )
                        )

            if collision:
                collisions.append(collision[0]) # TODO: Do we really always retrieve one?
            else:
                collisions.append(None)

        return collisions


    def generate_conflicts(timeslots):
        """
        Tests a list of timeslot objects for colliding timeslots in the database
        Returns a list of conflicts containing dicts of projected timeslots, collisions and solutions
        """

        conflicts = {}
        projected = []
        solutions = {}

        # Cycle each timeslot
        for ts in timeslots:

            # Contains one conflict: a projected timeslot, collisions and solutions
            conflict = {}

            # Contains collisions
            collisions = []

            # Contains possible solutions
            solution_choices = set()

            # Get collisions for each timeslot
            collision_list = list(TimeSlot.objects.filter(
                           ( Q(start__lt=ts.end) & Q(end__gte=ts.end) ) |
                           ( Q(end__gt=ts.start) & Q(end__lte=ts.end) ) |
                           ( Q(start__gte=ts.start) & Q(end__lte=ts.end) ) |
                           ( Q(start__lte=ts.start) & Q(end__gte=ts.end) )
                        ).order_by('start'))

            # Add the projected timeslot
            projected_entry = {}
            projected_entry['hash'] = ts.hash
            projected_entry['start'] = str(ts.start)
            projected_entry['end'] = str(ts.end)

            for c in collision_list:

                # Add the collision
                collision = {}
                collision['id'] = c.id
                collision['start'] = str(c.start)
                collision['end'] = str(c.end)
                collision['playlist_id'] = c.playlist_id
                collision['show'] = c.show.id
                collision['show_name'] = c.show.name
                collision['is_repetition'] = c.is_repetition
                collision['schedule'] = c.schedule_id
                collision['memo'] = c.memo

                # Get note
                try:
                    note = Note.objects.get(timeslot=c.id).values_list('id', flat=True)
                    collision['note_id'] = note
                except ObjectDoesNotExist:
                    pass

                collisions.append(collision)


                '''Determine acceptable solutions'''

                if len(collision_list) > 1:
                    # If there is more than one collision: Only these two are supported at the moment
                    solution_choices.add('theirs')
                    solution_choices.add('ours')
                else:
                    # These two are always possible: Either keep theirs and remove ours or vice versa
                    solution_choices.add('theirs')
                    solution_choices.add('ours')

                    # Partly overlapping: projected starts earlier than existing and ends earlier
                    #
                    #    ex.  pr.
                    #        +--+
                    #        |  |
                    #   +--+ |  |
                    #   |  | +--+
                    #   |  |
                    #   +--+
                    #
                    if ts.start < c.start and ts.end > c.start and ts.end <= c.end:
                        solution_choices.add('theirs-end')
                        solution_choices.add('ours-end')

                    # Partly overlapping: projected starts later than existing and ends later
                    #
                    #    ex.  pr.
                    #   +--+
                    #   |  |
                    #   |  | +--+
                    #   +--+ |  |
                    #        |  |
                    #        +--+
                    #
                    if ts.start >= c.start and ts.start < c.end and ts.end > c.end:
                        solution_choices.add('theirs-start')
                        solution_choices.add('ours-start')

                    # Fully overlapping: projected starts earlier and ends later than existing
                    #
                    #    ex.  pr.
                    #        +--+
                    #   +--+ |  |
                    #   |  | |  |
                    #   +--+ |  |
                    #        +--+
                    #
                    if ts.start < c.start and ts.end > c.end:
                        solution_choices.add('theirs-end')
                        solution_choices.add('theirs-start')
                        solution_choices.add('theirs-both')

                    # Fully overlapping: projected starts later and ends earlier than existing
                    #
                    #    ex.  pr.
                    #   +--+
                    #   |  | +--+
                    #   |  | |  |
                    #   |  | +--+
                    #   +--+
                    #
                    if ts.start > c.start and ts.end < c.end:
                        solution_choices.add('ours-end')
                        solution_choices.add('ours-start')
                        solution_choices.add('ours-both')

            if len(collisions) > 0:
                solutions[ts.hash] = ''

            projected_entry['collisions'] = collisions
            projected_entry['solution_choices'] = solution_choices
            projected.append(projected_entry)

        conflicts['projected'] = projected
        conflicts['solutions'] = solutions
        conflicts['notes'] = {}
        conflicts['playlists'] = {}

        return conflicts


    def make_conflicts(sdl, schedule_pk, show_pk):
        """
        Retrieves POST vars
        Generates a schedule
        Generates conflicts: Returns timeslots, collisions, solutions as JSON
        Returns conflicts dict
        """

        # Generate schedule
        schedule = Schedule.instantiate_upcoming(sdl, show_pk, schedule_pk)

        # Generate timeslots
        timeslots = Schedule.generate_timeslots(schedule)

        # Generate conflicts and add schedule
        conflicts = Schedule.generate_conflicts(timeslots)
        conflicts['schedule'] = model_to_dict(schedule)

        return conflicts


    def resolve_conflicts(data, schedule_pk, show_pk):
        """
        Resolves conflicts
        Expects JSON POST/PUT data from /shows/1/schedules/

        Returns a list of dicts if errors were found
        Returns an empty list if resolution was successful
        """

        sdl = data['schedule']
        solutions = data['solutions']

        # Regenerate conflicts
        schedule = Schedule.instantiate_upcoming(sdl, show_pk, schedule_pk)
        show = schedule.show
        conflicts = Schedule.make_conflicts(sdl, schedule.pk, show.pk)

        if schedule.rrule.freq > 0 and schedule.dstart == schedule.until:
            return {'detail': _("Start and until dates mustn't be the same")}

        if schedule.until < schedule.dstart:
            return {'detail': _("Until date mustn't before start")}

        num_conflicts = len([pr for pr in conflicts['projected'] if len(x['collisions']) > 0])

        if len(solutions) != num_conflicts:
            return {'detail': _("Numbers of conflicts and solutions don't match.")}

        # Projected timeslots to create
        create = []

        # Existing timeslots to update
        update = []

        # Existing timeslots to delete
        delete = []

        # Error messages
        errors = {}

        for ts in conflicts['projected']:

            # Ignore past dates
            if datetime.strptime(ts['start'], "%Y-%m-%d %H:%M:%S") <= datetime.today():
                continue

            # If no solution necessary
            #
            #     - Create the projected timeslot and skip
            #
            if not 'solution_choices' in ts or len(ts['collisions']) < 1:
                projected_ts = TimeSlot.objects.instantiate(ts['start'], ts['end'], schedule, show)
                create.append(projected_ts)
                continue

            # Check hash (if start, end, rrule or byweekday changed)
            if not ts['hash'] in solutions:
                errors[ts['hash']] = _("This change on the timeslot is not allowed.")
                continue

            # If no resolution given
            #
            #     - Skip
            #
            if solutions[ts['hash']] == '':
                errors[ts['hash']] = _("No solution given.")
                continue

            # If resolution is not accepted for this conflict
            #
            #     - Skip
            #
            if not solutions[ts['hash']] in ts['solution_choices']:
                errors[ts['hash']] = _("Given solution is not accepted for this conflict.")
                continue


            '''Conflict resolution'''

            existing = ts['collisions'][0]
            solution = solutions[ts['hash']]

            # theirs
            #
            #     - Discard the projected timeslot
            #     - Keep the existing collision(s)
            #
            if solution == 'theirs':
                continue


            # ours
            #
            #     - Create the projected timeslot
            #     - Delete the existing collision(s)
            #
            if solution == 'ours':
                projected_ts = TimeSlot.objects.instantiate(ts['start'], ts['end'], schedule, show)
                create.append(projected_ts)

                # Delete collision(s)
                for ex in ts['collisions']:
                    try:
                        existing_ts = TimeSlot.objects.get(pk=ex['id'])
                        delete.append(existing_ts)
                    except ObjectDoesNotExist:
                        pass


            # theirs-end
            #
            #     - Keep the existing timeslot
            #     - Create projected with end of existing start
            #
            if solution == 'theirs-end':
                projected_ts = TimeSlot.objects.instantiate(ts['start'], existing['start'], schedule, show)
                create.append(projected_ts)


            # ours-end
            #
            #     - Create the projected timeslot
            #     - Change the start of the existing collision to projected end
            #
            if solution == 'ours-end':
                projected_ts = TimeSlot.objects.instantiate(ts['start'], ts['end'], schedule, show)
                create.append(projected_ts)

                existing_ts = TimeSlot.objects.get(pk=existing['id'])
                existing_ts.start = datetime.strptime(ts['end'], '%Y-%m-%d %H:%M:%S')
                update.append(existing_ts)


            # theirs-start
            #
            #     - Keep existing
            #     - Create projected with start time of existing end
            #
            if solution == 'theirs-start':
                projected_ts = TimeSlot.objects.instantiate(existing['end'], ts['end'], schedule, show)
                create.append(projected_ts)


            # ours-start
            #
            #     - Create the projected timeslot
            #     - Change end of existing to projected start
            #
            if solution == 'ours-start':
                projected_ts = TimeSlot.objects.instantiate(ts['start'], ts['end'], schedule, show)
                create.append(projected_ts)

                existing_ts = TimeSlot.objects.get(pk=existing['id'])
                existing_ts.end = datetime.strptime(ts['start'], '%Y-%m-%d %H:%M:%S')
                update.append(existing_ts)


            # theirs-both
            #
            #     - Keep existing
            #     - Create two projected timeslots with end of existing start and start of existing end
            #
            if solution == 'theirs-both':
                projected_ts = TimeSlot.objects.instantiate(ts['start'], existing['start'], schedule, show)
                create.append(projected_ts)

                projected_ts = TimeSlot.objects.instantiate(existing['end'], ts['end'], schedule, show)
                create.append(projected_ts)


            # ours-both
            #
            #     - Create projected
            #     - Split existing into two:
            #       - Set existing end time to projected start
            #       - Create another one with start = projected end and end = existing end
            #
            if solution == 'ours-both':
                projected_ts = TimeSlot.objects.instantiate(ts['start'], ts['end'], schedule, show)
                create.append(projected_ts)

                existing_ts = TimeSlot.objects.get(pk=existing['id'])
                existing_ts.end = datetime.strptime(ts['start'], '%Y-%m-%d %H:%M:%S')
                update.append(existing_ts)

                projected_ts = TimeSlot.objects.instantiate(ts['end'], existing['end'], schedule, show)
                create.append(projected_ts)


        # If there were any errors, don't make any db changes yet
        # but add error messages and return already chosen solutions
        if len(errors) > 0:
            conflicts = Schedule.make_conflicts(model_to_dict(schedule), schedule.pk, show.pk)

            partly_resolved = conflicts['projected']
            saved_solutions = {}

            # Add already chosen resolutions and error message to conflict
            for index, c in enumerate(conflicts['projected']):

                # The element should only exist if there was a collision
                if len(c['collisions']) > 0:
                    saved_solutions[c['hash']] = ''

                if c['hash'] in solutions and solutions[c['hash']] in c['solution_choices']:
                    saved_solutions[c['hash']] = solutions[c['hash']]

                if c['hash'] in errors:
                    partly_resolved[index]['error'] = errors[c['hash']]

            # Re-insert post data
            conflicts['projected'] = partly_resolved
            conflicts['solutions'] = saved_solutions
            conflicts['notes'] = data['notes']
            conflicts['playlists'] = data['playlists']

            return conflicts


        # If 'dryrun' is true, just return the projected changes instead of executing them
        if 'dryrun' in sdl and sdl['dryrun']:
            output = {}
            output['create'] = [model_to_dict(ts) for ts in create]
            output['update'] = [model_to_dict(ts) for ts in update]
            output['delete'] = [model_to_dict(ts) for ts in delete]
            return output


        '''Database changes if no errors found'''

        # Only save schedule if timeslots were created
        if create:
            # Create or save schedule
            schedule.save()

            # Delete upcoming timeslots which still remain
            TimeSlot.objects.filter(schedule=schedule, start__gt=schedule.until).delete()

        # Update timeslots
        for ts in update:
            ts.save(update_fields=["start", "end"])

        # Create timeslots
        for ts in create:
            ts.schedule = schedule

            # Reassign playlists
            if 'playlists' in data and ts.hash in data['playlists']:
                ts.playlist_id = int(data['playlists'][ts.hash])

            ts.save()

            # Reassign notes
            if 'notes' in data and ts.hash in data['notes']:
                try:
                    note = Note.objects.get(pk=int(data['notes'][ts.hash]))
                    note.timeslot_id = ts.id
                    note.save(update_fields=["timeslot_id"])
                except ObjectDoesNotExist:
                    pass

        # Delete manually resolved timeslots
        for dl in delete:
            dl.delete()

        return model_to_dict(schedule)


    def save(self, *args, **kwargs):
        super(Schedule, self).save(*args, **kwargs)



class TimeSlotManager(models.Manager):
    @staticmethod
    def instantiate(start, end, schedule, show):
        return TimeSlot(start=datetime.strptime(start, '%Y-%m-%d %H:%M:%S'),
                        end=datetime.strptime(end, '%Y-%m-%d %H:%M:%S'),
                        show=show, is_repetition=schedule.is_repetition, schedule=schedule).generate()

    @staticmethod
    def get_or_create_current():
        try:
            return TimeSlot.objects.get(start__lte=datetime.now(), end__gt=datetime.now())
        except MultipleObjectsReturned:
            return TimeSlot.objects.filter(start__lte=datetime.now(), end__gt=datetime.now())[0]
        except ObjectDoesNotExist:
            once = RRule.objects.get(pk=1)
            today = date.today().weekday()
            default = Show.objects.get(pk=1)

            previous_timeslot = TimeSlot.objects.filter(end__lte=datetime.now()).order_by('-start')[0]
            next_timeslot = TimeSlot.objects.filter(start__gte=datetime.now())[0]

            dstart, tstart = previous_timeslot.end.date(), previous_timeslot.end.time()
            until, tend = next_timeslot.start.date(), next_timeslot.start.time()

            new_schedule = Schedule(rrule=once,
                                          byweekday=today,
                                          show=default,
                                          dstart=dstart,
                                          tstart=tstart,
                                          tend=tend,
                                          until=until)

            try:
                new_schedule.validate_unique()
                new_schedule.save()
            except ValidationError:
                pass
            else:
                return new_schedule.timeslots.all()[0]

    @staticmethod
    def get_day_timeslots(day):
        today = datetime.combine(day, time(6, 0))
        tomorrow = today + timedelta(days=1)

        return TimeSlot.objects.filter(Q(start__lte=today, end__gte=today) |
                                       Q(start__gt=today, start__lt=tomorrow)).exclude(end=today)

    @staticmethod
    def get_24h_timeslots(start):
        end = start + timedelta(hours=24)

        return TimeSlot.objects.filter(Q(start__lte=start, end__gte=start) |
                                       Q(start__gt=start, start__lt=end)).exclude(end=start)


    @staticmethod
    def get_7d_timeslots(start):
        start = datetime.combine(start, time(0, 0))
        end = start + timedelta(days=7)

        return TimeSlot.objects.filter(Q(start__lte=start, end__gte=start) |
                                       Q(start__gt=start, start__lt=end)).exclude(end=start)


    @staticmethod
    def get_timerange_timeslots(start, end):
        return TimeSlot.objects.filter(Q(start__lte=start, end__gte=start) |
                                       Q(start__gt=start, start__lt=end)).exclude(end=start)


class TimeSlot(models.Model):
    schedule = models.ForeignKey(Schedule, related_name='timeslots', verbose_name=_("Schedule"))
    start = models.DateTimeField(_("Start time")) # Removed 'unique=True' because new Timeslots need to be created before deleting the old ones (otherwise linked notes get deleted first)
    end = models.DateTimeField(_("End time"))
    show = models.ForeignKey(Show, editable=False, related_name='timeslots')
    memo = models.TextField(_("Memo"), blank=True)
    is_repetition = models.BooleanField(_("(REP)"), default=False)
    playlist_id = models.IntegerField(_("Playlist ID"), null=True)

    objects = TimeSlotManager()

    class Meta:
        ordering = ('start', 'end')
        verbose_name = _("Time slot")
        verbose_name_plural = _("Time slots")

    def __str__(self):
        start = self.start.strftime('%a, %d.%m.%Y %H:%M')
        end = self.end.strftime('%H:%M')
        is_repetition = ' ' + _('(REP)') if self.schedule.is_repetition is 1 else ''

        return '%s - %s  %s (%s)' % (start, end, is_repetition, self.show.name)

    def save(self, *args, **kwargs):
        self.show = self.schedule.show
        super(TimeSlot, self).save(*args, **kwargs)
        return self

    def generate(self, **kwargs):
        """Returns the object instance without saving"""

        self.show = self.schedule.show

        # Generate a distinct and reproducible hash for the timeslot
        # Makes sure none of these fields changed when updating
        string = str(self.start) + str(self.end) + str(self.schedule.rrule.id) + str(self.schedule.byweekday)
        self.hash = str(''.join(s for s in string if s.isdigit()))
        return self

    def get_absolute_url(self):
        return reverse('timeslot-detail', args=[str(self.id)])


class Note(models.Model):
    STATUS_CHOICES = (
        (0, _("Cancellation")),
        (1, _("Recommendation")),
        (2, _("Repetition")),
    )
    timeslot = models.OneToOneField(TimeSlot, verbose_name=_("Time slot"), unique=True)
    title = models.CharField(_("Title"), max_length=128, help_text=_("Give your note a good headline. What will your upcoming show be about? Try to arouse interest to listen to it!<br>Avoid technical data like the show's name, its airing times or its episode number. These data are added automatically."))
    slug = models.SlugField(_("Slug"), max_length=32, unique=True, help_text=_("A simple to read URL for your show."))
    summary = models.TextField(_("Summary"), blank=True, help_text=_("Describe your upcoming show in some sentences. Avoid technical data like airing times and contact information. They will be added automatically."))
    content = tinymce_models.HTMLField(_("Content"), help_text=_("Describe your upcoming show in detail."))
    ppoi = PPOIField('Image PPOI')
    height = models.PositiveIntegerField('Image Height', blank=True, null=True, editable=False)
    width = models.PositiveIntegerField('Image Width', blank=True, null=True,editable=False)
    image = VersatileImageField(_("Featured image"), blank=True, null=True, upload_to='note_images', width_field='width', height_field='height', ppoi_field='ppoi', help_text=_("Upload an image to your show. Images are automatically cropped around the 'Primary Point of Interest'. Click in the image to change it and press Save."))
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=1)
    start = models.DateTimeField(editable=False)
    show = models.ForeignKey(Show, related_name='notes', editable=True)
    cba_id = models.IntegerField(_("CBA ID"), blank=True, null=True, help_text=_("Link the note to a certain CBA post by giving its ID. (E.g. if your post's CBA URL is https://cba.fro.at/1234, then your CBA ID is 1234)"))
    audio_url = models.TextField(_("Direct URL to a linked audio file"), blank=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(User, editable=False, related_name='users', default=1)
    host = models.ForeignKey(Host, related_name='hosts', null=True)

    class Meta:
        ordering = ('timeslot',)
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def __str__(self):
        return '%s - %s' % (self.title, self.timeslot)

    def is_editable(self, note_id):
        """
        Whether the given note is assigned to a show the current user owns
        @return boolean
        """
        if self.request.user.is_superuser:
            return True

        return int(note_id) in self.request.user.shows.all().values_list('id', flat=True)

    def get_audio_url(cba_id):
        """
        Retrieve the direct URL to the mp3 in CBA
        In order to retrieve the URL, stations need
           - to be whitelisted by CBA
           - an API Key

        Therefore contact cba@fro.at
        """

        from pv.settings import CBA_AJAX_URL, CBA_API_KEY

        audio_url = ''

        if cba_id != None and cba_id != '' and CBA_API_KEY != '':
            from urllib.request import urlopen
            import json

            url = CBA_AJAX_URL + '?action=cba_ajax_get_filename&post_id=' + str(cba_id) + '&api_key=' + CBA_API_KEY

            # For momentary testing without being whitelisted - TODO: delete the line
            url = 'https://cba.fro.at/wp-content/plugins/cba/ajax/cba-get-filename.php?post_id=' + str(cba_id) + '&c=Ml3fASkfwR8'

            with urlopen(url) as conn:
                audio_url_json = conn.read().decode('utf-8-sig')
                audio_url = json.loads(audio_url_json)

        return audio_url


    def save(self, *args, **kwargs):
        self.start = self.timeslot.start
        self.show = self.timeslot.schedule.show

        super(Note, self).save(*args, **kwargs)

        # Generate thumbnails
        if self.image.name and settings.THUMBNAIL_SIZES:
            for size in settings.THUMBNAIL_SIZES:
                thumbnail = self.image.crop[size].name