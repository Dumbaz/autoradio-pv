from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from rest_framework_nested import routers
from rest_framework.authtoken import views
from oidc_provider import urls

from program.views import APIUserViewSet, APIHostViewSet, APIShowViewSet, APIScheduleViewSet, APITimeSlotViewSet, APINoteViewSet, APICategoryViewSet, APITypeViewSet, APITopicViewSet, APIMusicFocusViewSet, APIRTRCategoryViewSet, APILanguageViewSet, json_day_schedule, json_playout, json_timeslots_specials

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users', APIUserViewSet)
#router.register(r'owners', APIOwnerViewSet)
router.register(r'hosts', APIHostViewSet)
router.register(r'shows', APIShowViewSet)
router.register(r'schedules', APIScheduleViewSet)
router.register(r'timeslots', APITimeSlotViewSet)
router.register(r'notes', APINoteViewSet)
router.register(r'categories', APICategoryViewSet)
router.register(r'topics', APITopicViewSet)
router.register(r'types', APITypeViewSet)
router.register(r'musicfocus', APIMusicFocusViewSet)
router.register(r'rtrcategories', APIRTRCategoryViewSet)
router.register(r'languages', APILanguageViewSet)


'''Nested Routers'''

show_router = routers.NestedSimpleRouter(router, r'shows', lookup='show')

# /shows/1/schedules
show_router.register(r'schedules', APIScheduleViewSet, base_name='show-schedules')

# /shows/1/notes
show_router.register(r'notes', APINoteViewSet, base_name='show-notes')

# /shows/1/timeslots
show_router.register(r'timeslots', APITimeSlotViewSet, base_name='show-timeslots')
show_timeslot_router = routers.NestedSimpleRouter(show_router, r'timeslots', lookup='timeslot')

# /shows/1/timeslots/1/note/
show_timeslot_router.register(r'note', APINoteViewSet, base_name='show-timeslots-note')

# /shows/1/schedules
schedule_router = routers.NestedSimpleRouter(show_router, r'schedules', lookup='schedule')

# /shows/1/schedules/1/timeslots
schedule_router.register(r'timeslots', APITimeSlotViewSet, base_name='schedule-timeslots')
timeslot_router = routers.NestedSimpleRouter(schedule_router, r'timeslots', lookup='timeslot')

# /shows/1/schedules/1/timeslots/1/note
timeslot_router.register(r'note', APINoteViewSet, base_name='timeslots-note')


urlpatterns = [
    url(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    url(r'^api/v1/', include(router.urls) ),
    url(r'^api/v1/', include(show_router.urls)),
    url(r'^api/v1/', include(show_timeslot_router.urls)),
    url(r'^api/v1/', include(schedule_router.urls)),
    url(r'^api/v1/', include(timeslot_router.urls)),
    url(r'^api/v1/playout', json_playout),
    url(r'^api/v1/program/week', json_playout),
    url(r'^api/v1/program/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', json_day_schedule),
    url(r'^admin/', admin.site.urls),
    url(r'^program/', include('program.urls')),
    url(r'^nop', include('nop.urls')),
    url(r'^api/', include('frapp.urls')),
    #url(r'^tinymce/', include('tinymce.urls')),
    url(r'^export/timeslots_specials.json$', json_timeslots_specials),
]

if settings.DEBUG:
    urlpatterns.append(url(r'^site_media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}))