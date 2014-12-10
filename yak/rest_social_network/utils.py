from django.core.exceptions import ImproperlyConfigured
from django.apps import apps
from django.conf import settings


def get_social_model():
    """
    Returns the social model that is active in this project.
    """
    try:
        return apps.get_model(settings.SOCIAL_MODEL)
    except ValueError:
        raise ImproperlyConfigured("SOCIAL_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "SOCIAL_MODEL refers to model '%s' that has not been installed" % settings.SOCIAL_MODEL)
