from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from oauth2_provider.models import Application


def create_auth_client(sender, instance=None, created=False, **kwargs):
    """
    Intended to be used as a receiver function for a `post_save` signal on a custom User model
    Creates client_id and client_secret for authenicated users
    """
    if created:
        Application.objects.create(user=instance, client_type=Application.CLIENT_CONFIDENTIAL,
                                   authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS)


def reset_password(request, email, subject_template_name='users/password_reset_subject.txt',
                   rich_template_name='users/password_reset_email_rich.html',
                   template_name='users/password_reset_email.html'):
    """
    Inspired by Django's `PasswordResetForm.save()`. Extracted for reuse.
    Allows password reset emails to be sent to users with unusable passwords
    """
    from django.core.mail import send_mail
    UserModel = get_user_model()
    active_users = UserModel._default_manager.filter(email__iexact=email, is_active=True)
    for user in active_users:
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        c = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': 'http',  # Your site can handle its own redirects
        }
        subject = loader.render_to_string(subject_template_name, c)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        email = loader.render_to_string(template_name, c)
        html_email = loader.render_to_string(rich_template_name, c)
        send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_email)
