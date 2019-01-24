from django.conf.urls import url, include

from . import views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import verify_jwt_token
from django.contrib.auth.views import (
    password_reset,
    password_reset_done,
    password_reset_complete,
    password_reset_confirm,
    password_change,
    password_change_done)

router = DefaultRouter()
router.register(r'user', views.CustomUserViewSet)
router.register(r'profile', views.UserProfileViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    # url(r'^', include('django.contrib.auth.urls')),
    url(r'^password_change/', password_change, name='password_change'),
    url(r'^password_change/done/', password_change_done, name='password_change_done'),
    url(r'^password_reset/', password_reset, name='password_reset'),
    url(r'^password_reset/done/', password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/', password_reset_complete, name='password_reset_complete'),
    # url(r'^user', views.CustomUserViewSet.as_view({'get': 'list'})),
    # url(r'^profile', views.UserProfileViewSet.as_view({'get': 'list'})),
    url(r'^', include('rest_auth.urls')),
    url(r'^registration/', include('rest_auth.registration.urls')),
    url(r'^auth-token/', obtain_jwt_token),
    url(r'^refresh-token/', refresh_jwt_token),
    url(r'^verify-token/', verify_jwt_token)
]