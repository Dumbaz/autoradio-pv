from django.contrib import admin
from rest_framework import routers

admin.autodiscover()

urlpatterns = []

router = routers.DefaultRouter()
router.register(r'users', APIUserViewSet)