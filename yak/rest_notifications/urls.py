from django.conf.urls import url, include
from rest_framework import routers
from yak.rest_notifications.views import NotificationSettingViewSet, NotificationView, \
    NotificationFollowViewSet, NotificationLikeViewSet, NotificationShareViewSet, NotificationCommentViewSet, \
    PushwooshTokenView


router = routers.DefaultRouter()

router.register(r'notification_settings', NotificationSettingViewSet, base_name='notification_settings')
router.register(r'follows', NotificationFollowViewSet, base_name='follows')
router.register(r'likes', NotificationLikeViewSet, base_name='likes')
router.register(r'shares', NotificationShareViewSet, base_name='shares')
router.register(r'comments', NotificationCommentViewSet, base_name='comments')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^notifications/$', NotificationView.as_view(), name="notifications"),
    url(r'^pushwoosh_token/$', PushwooshTokenView.as_view(), name="pushwoosh_token"),
]
