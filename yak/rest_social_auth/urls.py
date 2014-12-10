from django.conf.urls import patterns, url
from yak.rest_social_auth import views


urlpatterns = patterns('',
    url(r'^social_sign_up/$', views.SocialSignUp.as_view(), name="social_sign_up"),
    url(r'^social_friends/$', views.SocialFriends.as_view(), name="social_friends"),
)
