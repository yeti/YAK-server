from django.conf.urls import patterns, url, include
from yak.rest_user import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, base_name='users')


urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^sign_up/$', views.SignUp.as_view(), name="sign_up"),
    url(r'^login/$', views.Login.as_view(), name="login"),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)
