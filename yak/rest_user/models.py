from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager


class AbstractYeti(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$', _('Enter a valid username.'), 'invalid')
        ])
    # Field name should be `fullname` instead of `full_name` for python-social-auth
    fullname = models.CharField(max_length=80, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    about = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    SIZES = {
        'thumbnail': {'height': 60, 'width': 60},
        'small_photo': {'height': 120, 'width': 120},
        'large_photo': {'height': 300, 'width': 300}
    }
    original_file_name = "original_photo"

    original_photo = models.ImageField(upload_to="user_photos/original/", blank=True, null=True)
    small_photo = models.ImageField(upload_to="user_photos/small/", blank=True, null=True)
    large_photo = models.ImageField(upload_to="user_photos/large/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="user_photos/thumbnail/", blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    # Used for `createsuperuser` command and nowhere else. Include any fields that cannot be blank
    REQUIRED_FIELDS = ['email']

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"{}".format(self.username)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.username = self.username.lower()

        if self.email:
            self.email = self.email.lower().strip()  # Remove leading or trailing white space
        if self.email == "":  # Allows unique=True to work without forcing email presence in forms
            self.email = None
        super(AbstractYeti, self).save(force_insert, force_update, using, update_fields)
