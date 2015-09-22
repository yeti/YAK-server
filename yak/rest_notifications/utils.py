import json
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from pypushwoosh import constants
from pypushwoosh.client import PushwooshClient
from yak.settings import yak_settings


class PushClient(PushwooshClient):
    def invoke(self, request):
        self.connection.request('POST', '/json/1.3/createMessage', request, self.headers)
        response = self.connection.getresponse()
        body = response.read()
        return json.loads(body)


def send_push_notification(receiver, message):
    client = PushClient()

    notifications = [{
        'content': message,
        'send_date': constants.SEND_DATE_NOW,
        'devices': [token.token for token in receiver.pushwoosh_tokens.all()],
        'ios_badges': '+1'
    }]

    request = {'request': {
        'notifications': notifications,
        'auth': yak_settings.PUSHWOOSH_AUTH_TOKEN,
        'application': yak_settings.PUSHWOOSH_APP_CODE
    }}
    request = json.dumps(request)

    return client.invoke(request)


def send_email_notification(receiver, message, reply_to=None):
    headers = {}
    if reply_to:
        headers['Reply-To'] = reply_to

    text_content = strip_tags(message)
    msg = EmailMultiAlternatives(yak_settings.EMAIL_NOTIFICATION_SUBJECT, text_content, settings.DEFAULT_FROM_EMAIL,
                                 [receiver.email], headers=headers)
    msg.attach_alternative(message, "text/html")
    msg.send()
