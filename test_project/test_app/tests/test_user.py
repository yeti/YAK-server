import base64
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.files.images import get_image_dimensions
from django.core.urlresolvers import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from test_project import settings
from test_project.test_app.tests.factories import UserFactory
from yak.rest_core.test import SchemaTestCase


User = get_user_model()


class UserTests(SchemaTestCase):
    def setUp(self):
        super(UserTests, self).setUp()
        self.user = User.objects.create_user(username='tester1', email='tester1@yeti.co', password='password')

    def test_autocomplete(self):
        """
        Tests that when a string is sent with the user's name or username, we return a filtered list of users
        """
        url = reverse("users-list")
        bob = UserFactory(username="bob")
        frank = UserFactory(username="frank")
        UserFactory(username="mindy")
        parameters = {"search": "fra"}
        response = self.assertSchemaGet(url, parameters, "$userResponse", bob)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["username"], frank.username)

    def test_update_user(self):
        me = UserFactory()
        stranger = UserFactory()
        url = reverse("users-detail", args=[me.pk])

        data = {
            "fullname": "Hodor",
            "username": me.username  # Don't freak out if unchanged unique data is sent
        }
        # Unauthenticated user can't update a user's profile
        self.assertSchemaPatch(url, "$userRequest", "$userResponse", data, None, unauthorized=True)
        self.assertEqual(User.objects.get(pk=me.pk).fullname, None)

        # Stranger can't update another user's profile
        self.assertSchemaPatch(url, "$userRequest", "$userResponse", data, stranger, unauthorized=True)
        self.assertEqual(User.objects.get(pk=me.pk).fullname, None)

        # User can update their own profile
        self.assertSchemaPatch(url, "$userRequest", "$userResponse", data, me)
        self.assertEqual(User.objects.get(pk=me.pk).fullname, "Hodor")

    def test_get_logged_in_user(self):
        me = UserFactory()
        UserFactory()

        url = reverse("users-me")
        response = self.assertSchemaGet(url, None, "$userResponse", me)
        self.assertEqual(response.data["id"], me.pk)

    def test_user_can_sign_up(self):
        url = reverse("sign_up")
        password = base64.encodestring("testtest")
        data = {
            "fullname": "tester",
            "username": "tester",
            "password": password
        }
        self.assertSchemaPost(url, "$signUpRequest", "$signUpResponse", data, None)
        user = User.objects.filter(username="tester")
        self.assertEqual(user.count(), 1)

        # Password gets decoded and hashed
        self.assertTrue(user[0].check_password("testtest"))

    def test_password_min_length(self):
        url = reverse("sign_up")
        password = base64.encodestring("test")
        data = {
            "fullname": "tester2",
            "username": "tester2",
            "email": "tester2@yeti.co",
            "password": password
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_user_can_log_in(self):
        url = reverse("login")

        # With the correct username and password, a user can log in with basic auth
        auth_string = base64.encodestring("tester1:password")
        self.client.credentials(HTTP_AUTHORIZATION='Basic ' + auth_string)
        response = self.client.get(url)
        self.assertValidJSONResponse(response)
        self.check_response_data(response, "$loginResponse")

        # Incorrect credentials return unauthorized
        auth_string = base64.encodestring("tester1:WRONGPASSWORD")
        self.client.credentials(HTTP_AUTHORIZATION='Basic ' + auth_string)
        response = self.client.get(url)
        self.assertHttpUnauthorized(response)

    def test_inexact_signup(self):
        """
        Email and username are case insensitive
        """
        UserFactory(username="used", email="used@email.com")
        url = reverse("sign_up")

        data = {
            'username': 'useD',
            'email': 'different@email.com',
            'password': "password"
        }
        response = self.client.post(url, data, format="json")
        self.assertHttpBadRequest(response)

        data = {'username': "new_username", 'email': 'useD@email.com', 'password': "password"}
        response = self.client.post(url, data, format="json")
        self.assertHttpBadRequest(response)

    def test_inexact_login(self):
        url = reverse("login")

        # username is case-insensitive for login
        auth_string = base64.encodestring("Tester1:password")
        self.client.credentials(HTTP_AUTHORIZATION='Basic ' + auth_string)
        response = self.client.get(url)
        self.assertValidJSONResponse(response)
        self.check_response_data(response, "$loginResponse")

    def test_edit_user_to_inexact_match(self):
        """
        You also can't edit a user to an inexact match of someone else's username. This fails correctly at the DB level,
        but need to add validation in the API to give better errors
        """
        user1 = UserFactory(username="baylee")
        UserFactory(username="winnie")

        url = reverse("users-detail", args=[user1.pk])
        data = {"username": "Winnie"}
        self.add_credentials(user1)
        response = self.client.patch(url, data, format="json")
        self.assertHttpBadRequest(response)

    def test_user_can_get_token(self):
        """
        Below is the test I want. But it fails because django-oauth-toolkit will only accept requests with
        content-type application/x-www-form-urlencoded. DRF does not appear to support this type.

        url = reverse("oauth2_provider:token")
        data = {
            "client_id": self.user.application_set.first().client_id,
            "client_secret": self.user.application_set.first().client_secret,
            "grant_type": "client_credentials"
        }
        self.assertManticomPOSTResponse(url, "$tokenRequest", "$tokenResponse", data, None)
        """
        pass

    def test_token_authenticates_user(self):
        pass

    def test_photo_resize(self):
        me = UserFactory()
        url = reverse("users-detail", args=[me.pk])
        data = {
            "original_photo": open(settings.PROJECT_ROOT + "/test_app/tests/img/yeti.jpg", 'r')
        }
        self.assertSchemaPatch(url, "$userRequest", "$userResponse", data, me, format="multipart")
        user = User.objects.get(pk=me.pk)

        # Check the original photo is saved
        self.assertEqual(
            user.original_photo.file.read(),
            open(settings.PROJECT_ROOT + "/test_app/tests/img/yeti.jpg", 'r').read()
        )

        # Check the photo is correctly resized
        for size_field, size in User.SIZES.iteritems():
            w, h = get_image_dimensions(getattr(user, size_field).file)
            self.assertEqual(size['height'], h)
            self.assertEqual(size['width'], w)


class PasswordResetTests(SchemaTestCase):

    def test_user_can_change_password(self):
        felicia = UserFactory(username='felicia')
        felicia.set_password('password')
        felicia.save()
        url = reverse("password_change")

        data = {
            "old_password": base64.encodestring("password"),
            "password": base64.encodestring("felicia"),
            "confirm_password": base64.encodestring("felicia")
        }
        # Unauthenticated user can't change password
        self.assertSchemaPatch(url, "$changePasswordRequest", "$changePasswordResponse", data, None, unauthorized=True)
        self.assertFalse(User.objects.get(pk=felicia.pk).check_password("felicia"))

        # User can't change password if the old / current password is incorrect
        bad_data = {
            "old_password": base64.encodestring("wrong_password"),
            "password": base64.encodestring("felicia"),
            "confirm_password": base64.encodestring("felicia")
        }
        self.assertSchemaPatch(url, "$changePasswordRequest", "$changePasswordResponse", bad_data, felicia,
                               unauthorized=True)
        self.assertFalse(User.objects.get(pk=felicia.pk).check_password("felicia"))

        # User can't change password if the two new passwords don't match
        mismatch_password_data = {
            "old_password": base64.encodestring("password"),
            "password": base64.encodestring("felicia"),
            "confirm_password": base64.encodestring("FELICIA")
        }
        self.add_credentials(felicia)
        response = self.client.patch(url, mismatch_password_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.get(pk=felicia.pk).check_password("felicia"))

        # User can change their own password
        self.assertSchemaPatch(url, "$changePasswordRequest", "$changePasswordResponse", data, felicia)
        self.assertTrue(User.objects.get(pk=felicia.pk).check_password("felicia"))

    def test_user_can_get_reset_password_email(self):
        jeanluc = UserFactory(username="jeanluc")
        url = reverse("password_reset")
        data = {
            "email": jeanluc.email
        }
        self.assertSchemaPost(url, "$resetPasswordRequest", "$resetPasswordResponse", data, None, status_OK=True)
        self.assertEqual(len(mail.outbox), 1)

    def test_user_can_reset_password(self):
        url = reverse("password_new")
        beverly = UserFactory(username="beverly")
        beverly.set_password("jack")
        beverly.save()

        mismatch_password_data = {
            "uid": urlsafe_base64_encode(force_bytes(beverly.pk)),
            "token": default_token_generator.make_token(beverly),
            "password": base64.encodestring("wesley"),
            "confirm_password": base64.encodestring("WESLEY")
        }
        response = self.client.post(url, mismatch_password_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.get(username='beverly').check_password('wesley'))

        bad_uid_data = {
            "uid": urlsafe_base64_encode(force_bytes(UserFactory().pk)),
            "token": default_token_generator.make_token(beverly),
            "password": base64.encodestring("wesley"),
            "confirm_password": base64.encodestring("wesley")
        }
        response = self.client.post(url, bad_uid_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.get(username='beverly').check_password('wesley'))

        good_data = {
            "uid": urlsafe_base64_encode(force_bytes(beverly.pk)),
            "token": default_token_generator.make_token(beverly),
            "password": base64.encodestring("wesley"),
            "confirm_password": base64.encodestring("wesley")
        }
        self.assertSchemaPost(url, "$setPasswordRequest", "$userResponse", good_data, None, status_OK=True)
        self.assertTrue(User.objects.get(username='beverly').check_password('wesley'))
