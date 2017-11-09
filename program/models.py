from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError, MultipleObjectsReturned
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from versatileimagefield.fields import VersatileImageField, PPOIField
from django.conf import settings

from tinymce import models as tinymce_models

from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule


from .utils import get_automation_id_choices


class Type(models.Model):
    type = models.CharField(_("Type"), max_length=32)
    slug = models.SlugField(_("Slug"), max_length=32, unique=True)
    color = models.CharField(_("Color"), max_length=7, default='#ffffff')
    text_color = models.CharField(_("Text color"), max_length=7, default='#000000')
    enabled = models.BooleanField(_("Enabled"), default=True)

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

    class Meta:
        ordering = ('rtrcategory',)
        verbose_name = _("RTR Category")
        verbose_name_plural = _("RTR Categories")

    def __str__(self):
        return '%s' % self.rtrcategory


class Host(models.Model):
    name = models.CharField(_("Name"), max_length=128)
    is_always_visible = models.BooleanField(_("Is always visible"), default=False)
    email = models.EmailField(_("E-Mail"), blank=True)
    website = models.URLField(_("Website"), blank=True)

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


class Show(models.Model):
    predecessor = models.ForeignKey('self', blank=True, null=True, related_name='successors', verbose_name=_("Predecessor"))
    hosts = models.ManyToManyField(Host, blank=True, related_name='shows', verbose_name=_("Hosts"))
    owners = models.ManyToManyField(User, blank=True, related_name='shows', verbose_name=_("Owners"))
    type = models.ForeignKey(Type, related_name='shows', verbose_name=_("Type"))
    category = models.ManyToManyField(Category, blank=True, related_name='shows', verbose_name=_("Category"))
    rtrcategory = models.ForeignKey(RTRCategory, related_name='shows', verbose_name=_("RTR Category"))
    topic = models.ManyToManyField(Topic, blank=True, related_name='shows', verbose_name=_("Topic"))
    musicfocus = models.ManyToManyField(MusicFocus, blank=True, related_name='shows', verbose_name=_("Music focus"))
    name = models.CharField(_("Name"), max_length=255)
    slug = models.CharField(_("Slug"), max_length=255, unique=True)
    ppoi = PPOIField('Image PPOI')
    height = models.PositiveIntegerField('Image Height', blank=True, null=True, editable=False)
    width = models.PositiveIntegerField('Image Width', blank=True, null=True,editable=False)
    image = VersatileImageField(_("Image"), blank=True, null=True, upload_to='show_images', width_field='width', height_field='height', ppoi_field='ppoi')
    logo = models.ImageField(_("Logo"), blank=True, null=True, upload_to='show_images')
    short_description = models.CharField(_("Short description"), max_length=64)
    description = tinymce_models.HTMLField(_("Description"), blank=True, null=True)
    email = models.EmailField(_("E-Mail"), blank=True, null=True)
    website = models.URLField(_("Website"), blank=True, null=True)
    cba_series_id = models.IntegerField(_("CBA Series ID"), blank=True, null=True)
    fallback_pool = models.CharField(_("Fallback Pool"), max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('slug',)
        verbose_name = _("Show")
        verbose_name_plural = _("Shows")

    def __str__(self):
        return '%04d | %s' % (self.id, self.name)

    def get_absolute_url(self):
        return reverse('show-detail', args=[self.slug])

    # Called by show templates
    def active_schedules(self):
        return self.schedules.filter(until__gt=date.today())


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
    fallback_playlist = models.IntegerField(_("Fallback Playlist"), blank=True, null=True)
    automation_id = models.IntegerField(_("Automation ID"), blank=True, null=True, choices=get_automation_id_choices()) # Deprecated
    created = models.DateTimeField(auto_now_add=True, editable=False, null=True) #-> both see https://stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add
    last_updated = models.DateTimeField(auto_now=True, editable=False, null=True)

    class Meta:
        ordering = ('dstart', 'tstart')
        # Produces error when adding several schedules at the same time.
        # Do this test in another way, since it is quite unspecific anyway
        #unique_together = ('rrule', 'byweekday', 'dstart', 'tstart')
        verbose_name = _("Program slot")
        verbose_name_plural = _("Program slots")

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

    def generate_timeslots(schedule):
        """
        Returns a list of timeslot objects based on a schedule and its rrule
        Returns past timeslots as well starting from dstart (not today)
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
            print(str(starts[k]) + ' - ' + str(ends[k]))

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


    def save(self, *args, **kwargs):
        # TODO: Test if auto_now_add and auto_now really always work
        #if not self.id or self.id == None:
        #    self.created = datetime.today()

        super(Schedule, self).save(*args, **kwargs)



class TimeSlotManager(models.Manager):
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


class TimeSlot(models.Model):
    schedule = models.ForeignKey(Schedule, related_name='timeslots', verbose_name=_("Schedule"))
    start = models.DateTimeField(_("Start time")) # Removed 'unique=True' because new Timeslots need to be created before deleting the old ones (otherwise linked notes get deleted first)
    end = models.DateTimeField(_("End time"))
    show = models.ForeignKey(Show, editable=False, related_name='timeslots')

    objects = TimeSlotManager()

    class Meta:
        ordering = ('start', 'end')
        verbose_name = _("Time slot")
        verbose_name_plural = _("Time slots")

    def __str__(self):
        start = self.start.strftime('%d.%m.%Y %H:%M')
        end = self.end.strftime('%H:%M')

        return '%s - %s  |  %s' % (start, end, self.show.name)

    def save(self, *args, **kwargs):
        self.show = self.schedule.show
        super(TimeSlot, self).save(*args, **kwargs)
        return self;

    def generate(self, **kwargs):
        """Returns the object instance without saving"""
        self.show = self.schedule.show
        return self;

    def get_absolute_url(self):
        return reverse('timeslot-detail', args=[str(self.id)])


class Note(models.Model):
    STATUS_CHOICES = (
        (0, _("Cancellation")),
        (1, _("Recommendation")),
        (2, _("Repetition")),
    )
    timeslot = models.OneToOneField(TimeSlot, verbose_name=_("Time slot"), unique=True)
    title = models.CharField(_("Title"), max_length=128)
    slug = models.SlugField(_("Slug"), max_length=32, unique=True)
    summary = tinymce_models.HTMLField(_("Summary"), blank=True)
    content = tinymce_models.HTMLField(_("Content"))
    ppoi = PPOIField('Image PPOI')
    height = models.PositiveIntegerField('Image Height', blank=True, null=True, editable=False)
    width = models.PositiveIntegerField('Image Width', blank=True, null=True,editable=False)
    image = VersatileImageField(_("Featured image"), blank=True, null=True, upload_to='note_images', width_field='width', height_field='height', ppoi_field='ppoi')
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=1)
    start = models.DateTimeField(editable=False)
    show = models.ForeignKey(Show, editable=False, related_name='notes')
    cba_id = models.IntegerField(_("CBA ID"), blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(User, editable=False, related_name='users', default=1)

    class Meta:
        ordering = ('timeslot',)
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def __str__(self):
        return '%s - %s' % (self.title, self.timeslot)

    def save(self, *args, **kwargs):
        self.start = self.timeslot.start
        self.show = self.timeslot.schedule.show

        super(Note, self).save(*args, **kwargs)

        # Generate thumbnails
        if self.image.name and settings.THUMBNAIL_SIZES:
            for size in settings.THUMBNAIL_SIZES:
                thumbnail = self.image.crop[size].name