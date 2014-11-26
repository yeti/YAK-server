from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from pypushwoosh.client import PushwooshClient
from pypushwoosh.command import CreateTargetedMessageCommand
from pypushwoosh.filter import ApplicationFilter
from yak.settings import yak_settings


def send_push_notification(receiver, message):
    command = CreateTargetedMessageCommand()
    command.auth = yak_settings.PUSHWOOSH_AUTH_TOKEN
    command.devices_filter = ApplicationFilter(yak_settings.PUSHWOOSH_APP_CODE)
    # TODO: I don't think this is actually limiting the devices sent to
    command.devices = [token.token for token in receiver.pushwoosh_tokens.all()]
    command.content = message

    client = PushwooshClient()
    return client.invoke(command)


def send_email_notification(receiver, message, reply_to=None):
    headers = {}
    if reply_to:
        headers['Reply-To'] = reply_to

    text_content = strip_tags(message)
    msg = EmailMultiAlternatives(yak_settings.EMAIL_NOTIFICATION_SUBJECT, text_content, settings.DEFAULT_FROM_EMAIL,
                                 [receiver.email], headers=headers)
    msg.attach_alternative(message, "text/html")
    msg.send()
