from django.conf.urls import url, include
from yak.rest_user import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, base_name='users')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^sign_up/$', views.SignUp.as_view(), name="sign_up"),
    url(r'^login/$', views.Login.as_view(), name="login"),
    url(r'^sign_in/$', views.SignIn.as_view(), name="sign_in"),
    url(r'^password/change/$', views.PasswordChangeView.as_view(), name="password_change"),
    url(r'^password/reset/$', views.PasswordResetView.as_view(), name="password_reset"),
    url(r'^password/new/$', views.PasswordSetView.as_view(), name="password_new"),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
