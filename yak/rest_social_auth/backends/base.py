import abc


class ExtraDataAbstractMixin(object):
    """
    Ensure that backends define these methods
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_extra_data(response, user):
        return

    @abc.abstractmethod
    def get_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
        return