from django.conf.urls.defaults import *
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from models import Host, Show, TimeSlot
from views import RecommendationsView, RecommendationsBoxView, ShowListView

urlpatterns = patterns('',
    url('^hosts/$', ListView.as_view(model=Host,context_object_name='host_list')),
    url('^host/(?P<pk>\d+)/$', DetailView.as_view(model=Host), name='host-detail'),
    url('^recommendations/$', RecommendationsView.as_view()),
    url('^recommendations_box/$', RecommendationsBoxView.as_view()),
    url('^shows/$', ShowListView.as_view()),
    url('^show/(?P<slug>[\w-]+)/$', DetailView.as_view(model=Show), name='show-detail'),
    url('^timeslot/(?P<pk>\d+)/$', DetailView.as_view(model=TimeSlot, context_object_name='timeslot'), name='timeslot-detail'),
)