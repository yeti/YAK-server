from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from .test_app.api.views import ProjectUserViewSet, PostViewSet


router = routers.DefaultRouter()
router.register(r'users', ProjectUserViewSet, base_name='users')
router.register(r'posts', PostViewSet, base_name='posts')

api_v1 = [

    # Project-specific views
    url(r'^', include(router.urls)),

    # Auth views
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include('social_django.urls', namespace='social')),

    # Library views
    url(r'^', include('yak.rest_user.urls')),
    url(r'^', include('yak.rest_social_auth.urls')),
    url(r'^', include('yak.rest_social_network.urls')),
    url(r'^', include('yak.rest_notifications.urls')),
]


admin.autodiscover()

urlpatterns = [
    # Change the admin prefix here to use an alternate URL for the
    # admin interface, which would be marginally more secure.
    url(r'^admin/', admin.site.urls),
]

urlpatterns += [
    url(r'^api/v1/', include(api_v1)),
]
