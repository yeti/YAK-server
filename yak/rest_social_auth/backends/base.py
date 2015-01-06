import abc


class ExtraDataAbstractMixin(object):
    """
    Ensure that backends define these methods. Used in pipeline to save extra data on the user model.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_extra_data(response, user):
        return

    @abc.abstractmethod
    def get_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
        return


class ExtraActionsAbstractMixin(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def post(user_social_auth, social_obj):
        return

    @abc.abstractmethod
    def get_friends(user_social_auth):
        return
