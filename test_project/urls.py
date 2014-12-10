from __future__ import unicode_literals

from django.conf.urls import patterns
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from test_app.api.views import ProjectUserViewSet


router = routers.DefaultRouter()
# router.register(r'clips', ClipViewSet, base_name='clips')
# router.register(r'sessions', SessionViewSet, base_name='sessions')
# router.register(r'videos', VideoViewSet, base_name='videos')
# router.register(r'castings', CastingViewSet, base_name='castings')
router.register(r'users', ProjectUserViewSet, base_name='users')
# router.register(r'locations', LocationViewSet, base_name='locations')

ap1_v1 = patterns('',

    # Project-specific views
    url(r'^', include(router.urls)),

    # Auth views
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('^', include('social.apps.django_app.urls', namespace='social')),

    # Library views
    url(r'^', include('yak.rest_user.urls')),
    url(r'^', include('yak.rest_social_auth.urls')),
    url(r'^', include('yak.rest_social_network.urls')),
    url(r'^', include('yak.rest_notifications.urls')),
)


admin.autodiscover()

urlpatterns = i18n_patterns("",
    # Change the admin prefix here to use an alternate URL for the
    # admin interface, which would be marginally more secure.
    ("^admin/", include(admin.site.urls)),
)

urlpatterns += patterns('',

    # Web views
    # url(r'^(?P<content_type>\w+)/(?P<encoded_id>[a-zA-Z0-9]+)/$', 'brochure.views.share', name='share'),

    url(r'^api/v1/', include(ap1_v1)),
)