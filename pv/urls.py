from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve

from program.views import json_day_schedule, json_week_schedule, json_timeslots_specials, json_get_timeslot, json_get_timeslots_by_show

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^program/', include('program.urls')),
    url(r'^nop', include('nop.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^export/day_schedule/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', json_day_schedule),
    url(r'^export/week_schedule$', json_week_schedule),
    url(r'^export/timeslots_specials.json$', json_timeslots_specials),
    url(r'^export/get_timeslot$', json_get_timeslot, name='get-timeslot'),
    url(r'^export/get_timeslots_by_show$', json_get_timeslots_by_show, name='get-timeslots-by-show'),
]

if settings.DEBUG:
    urlpatterns.append(url(r'^site_media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}))