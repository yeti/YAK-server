import json

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils.module_loading import import_string
from pypushwoosh import constants
from pypushwoosh.client import PushwooshClient

from yak.settings import yak_settings


def submit_to_pushwoosh(request_data):
    url = 'https://cp.pushwoosh.com/json/1.3/createMessage'
    response = requests.post(url, data=request_data, headers=PushwooshClient.headers)
    return response.json()


def send_pushwoosh_notification(receiver, message, deep_link=None):
    notification_data = {
        'content': message,
        'send_date': constants.SEND_DATE_NOW,
        'devices': [token.token for token in receiver.pushwoosh_tokens.all()],
        'ios_badges': '+1'
    }

    if deep_link is not None:
        notification_data['minimize_link'] = 0
        notification_data['link'] = deep_link

    request = {'request': {
        'notifications': [notification_data],
        'auth': yak_settings.PUSHWOOSH_AUTH_TOKEN,
        'application': yak_settings.PUSHWOOSH_APP_CODE
    }}

    request_data = json.dumps(request)

    return submit_to_pushwoosh(request_data)


def send_push_notification(receiver, message, deep_link=None):
    notification_handler = import_string(yak_settings.PUSH_NOTIFICATION_HANDLER)
    return notification_handler(receiver, message, deep_link=None)


def send_email_notification(receiver, message, reply_to=None):
    headers = {}
    if reply_to:
        headers['Reply-To'] = reply_to

    text_content = strip_tags(message)
    msg = EmailMultiAlternatives(yak_settings.EMAIL_NOTIFICATION_SUBJECT, text_content, settings.DEFAULT_FROM_EMAIL,
                                 [receiver.email], headers=headers)
    msg.attach_alternative(message, "text/html")
    msg.send()
