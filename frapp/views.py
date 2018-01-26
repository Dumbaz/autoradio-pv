import json
from datetime import date, datetime, time

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site

from program.models import Note, Show, Category, TimeSlot, Host, Schedule


def generate_frapp_broadcastinfos(schedule):
    """
    Generate broadcast infos according to FRAPP datamodel
    Returns a string
    """

    # Don't translate!
    weekdays = ('Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag')

    broadcasttime = schedule.tstart.strftime('%H:%M') + ' - ' + schedule.tend.strftime('%H:%M') + ' Uhr;'
    broadcastinfos = ''

    if schedule.rrule_id == 1: # Once
        broadcastinfos = 'Am ' + weekdays[schedule.byweekday] + ', ' + schedule.dstart.strftime('%d.%m.%Y') + ', ' + broadcasttime
    if schedule.rrule_id == 2: # Daily
        broadcastinfos = 'täglich, ' + broadcasttime
    if schedule.rrule_id == 3: # Business days
        broadcastinfos = 'werktags, ' + broadcasttime
    if schedule.rrule_id == 4: # Weekly
        broadcastinfos = 'Jeden ' + weekdays[schedule.byweekday] + ', ' + broadcasttime
    if schedule.rrule_id == 5: # Bi-weekly
        print("Not supported by FRAPP yet")
    if schedule.rrule_id == 6: # Every four weeks
        print("Not supported by FRAPP yet")
    if schedule.rrule_id == 7: # Even calendar weeks
       broadcastinfos = 'Jeden geraden ' + weekdays[schedule.byweekday] + ', ' + broadcasttime
    if schedule.rrule_id == 8: # Odd calendar weeks
       broadcastinfos = 'Jeden ungeraden ' + weekdays[schedule.byweekday] + ', ' + broadcasttime
    if schedule.rrule_id == 9: # Every 1st week
       broadcastinfos = 'Jeden 1. ' + weekdays[schedule.byweekday] + ', ' + broadcasttime
    if schedule.rrule_id == 10: # Every 2nd week
       broadcastinfos = 'Jeden 2. ' + weekdays[schedule.byweekday] + ', ' + broadcasttime
    if schedule.rrule_id == 11: # Every 3rd week
       broadcastinfos = 'Jeden 3. ' + weekdays[schedule.byweekday] + ', ' + broadcasttime
    if schedule.rrule_id == 12: # Every 4th week
       broadcastinfos = 'Jeden 4. ' + weekdays[schedule.byweekday] + ', ' + broadcasttime
    if schedule.rrule_id == 13: # Every 5th week
       broadcastinfos = 'Jeden 5. ' + weekdays[schedule.byweekday] + ', ' + broadcasttime

    return broadcastinfos


def json_frapp(request):
    """
    Expects GET variable 'date' (date), otherwise date will be today

    Returns 3 JSON objects:
        - categories: A list of all existing categories
        - series: A list of shows for the given date
        - shows: A list of timeslots for the given date including notes
    """
    from pv.settings import MEDIA_URL

    if request.GET.get('date') == None:
        start = datetime.combine(date.today(), time(0, 0))
    else:
        start = datetime.combine( datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date(), time(0, 0))

    end = datetime.combine(start, time(23, 59))

    timeslots = TimeSlot.objects.filter(start__gte=start,start__lte=end).select_related('show').order_by('start')


    '''Generate categories object for output'''

    categories = Category.objects.all()
    categories_output = []

    for c in categories:
        c_entry = {
            'id': c.id,
            'color': c.color.replace('#', '').upper(),
            'namedisplay': c.category,
            'description': c.description
        }

        categories_output.append(c_entry)

    # Get all series for timeslots
    series = set()
    for ts in timeslots:
        series.add(ts.show)


    '''Generate series object for output'''

    series_output = []

    for s in series:
        metainfos = []
        metainfos.append({ 'key': 'ProduzentIn', 'value': ', '.join(ts.show.hosts.values_list('name', flat=True)) })
        metainfos.append({ 'key': 'E-Mail', 'value': ', '.join(ts.show.hosts.values_list('email', flat=True)) })

        image = '' if s.image.name == None or s.image.name == '' else str(get_current_site(request)) + MEDIA_URL + s.image.name
        url = '' if s.website == None or s.website == '' else s.website

        # Get active schedules for the given date
        # But include upcoming single timeslots (with rrule_id=1)
        schedules = Schedule.objects.filter( Q(show=s.id,is_repetition=False) &
                                             (
                                               Q(rrule_id__gt=1,dstart__lte=start,until__gte=start) |
                                               Q(rrule_id=1,dstart__gte=start)
                                             )
                                           )

        schedules_repetition = Schedule.objects.filter( Q(show=s.id,is_repetition=True) &
                                             (
                                               Q(rrule_id__gt=1,dstart__lte=start,until__gte=start) |
                                               Q(rrule_id=1,dstart__gte=start)
                                             )
                                           )

        broadcastinfos = ''

        if not schedules.exists():
            continue

        for schedule in schedules:
            broadcastinfos = broadcastinfos + generate_frapp_broadcastinfos(schedule)

        if schedules_repetition.exists():
            broadcastinfos = broadcastinfos + 'Wiederholung jeweils:'
            for schedule in schedules_repetition:
                broadcastinfos = broadcastinfos + generate_frapp_broadcastinfos(schedule)

        s_entry = {
            'id': s.id,
            'categoryid': s.category.values_list('id', flat=True)[0],
            'color': s.category.values_list('color', flat=True)[0].replace('#', '').upper(),
            'namedisplay': s.name,
            'description': s.description,
            'url': url,
            'image': image,
            'broadcastinfos': broadcastinfos,
            'metainfos': metainfos
        }

        series_output.append(s_entry)


    '''Generate shows object for output'''

    shows_output = []

    for ts in timeslots:

        is_repetition = ' ' + _('REP') if ts.schedule.is_repetition is 1 else ''
        namedisplay = ts.show.name + is_repetition
        description = ts.show.description
        url = str(get_current_site(request)) + '/shows/' + ts.show.slug
        urlmp3 = ''

        # If there's a note to the timeslot use its title, description and url
        try:
            note = Note.objects.get(timeslot=ts.id)
            namedisplay = note.title + is_repetition
            description = note.content
            url = str(get_current_site(request)) + '/notes/' + note.slug
            urlmp3 = note.audio_url
        except ObjectDoesNotExist:
            pass

        ts_entry = {
            'id': ts.id,
            'seriesid': ts.show.id,
            'datetimestart': ts.start.strftime('%d.%m.%Y %H:%M:%S'),
            'datetimeend': ts.end.strftime('%d.%m.%Y %H:%M:%S'),
            'namedisplay': namedisplay,
            'description': description,
            'url': url,
            'urlmp3': urlmp3,
        }

        shows_output.append(ts_entry)

    output = {}
    output['categories'] = categories_output
    output['series'] = series_output
    output['shows'] = shows_output

    return HttpResponse(json.dumps(output, ensure_ascii=False).encode('utf8'),
                        content_type="application/json; charset=utf-8")