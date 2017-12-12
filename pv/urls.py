from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from rest_framework import routers
from rest_framework.authtoken import views

from program.views import APIUserViewSet, APIHostViewSet, APIShowViewSet, APITimeSlotViewSet, APINoteViewSet, APICategoryViewSet, APITypeViewSet, APITopicViewSet, APIMusicFocusViewSet, APIRTRCategoryViewSet, APILanguageViewSet, json_day_schedule, json_week_schedule, json_timeslots_specials, json_get_timeslots_by_show

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users', APIUserViewSet)
#router.register(r'owners', APIOwnerViewSet)
router.register(r'hosts', APIHostViewSet)
router.register(r'shows', APIShowViewSet)
router.register(r'timeslots', APITimeSlotViewSet)
router.register(r'notes', APINoteViewSet)
router.register(r'categories', APICategoryViewSet)
router.register(r'topics', APITopicViewSet)
router.register(r'types', APITypeViewSet)
router.register(r'musicfocus', APIMusicFocusViewSet)
router.register(r'rtrcategories', APIRTRCategoryViewSet)
router.register(r'languages', APILanguageViewSet)

urlpatterns = [
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^api/v1/', include(router.urls) ),
    url(r'^api/v1/program$', json_week_schedule),
    url(r'^api/v1/timeslots-by-show$', json_get_timeslots_by_show, name='json_get_timeslots_by_show'),
    url(r'^api/v1/week_schedule$', json_week_schedule),
    url(r'^admin/', admin.site.urls),
    url(r'^program/', include('program.urls')),
    url(r'^nop', include('nop.urls')),
    #url(r'^tinymce/', include('tinymce.urls')),
    url(r'^export/day_schedule/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', json_day_schedule),
    url(r'^export/timeslots_specials.json$', json_timeslots_specials),
]

if settings.DEBUG:
    urlpatterns.append(url(r'^site_media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}))