import base64
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
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
            "fullname": "Hodor"
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
            "username": "tester",
            "email": "tester@yetihq.com",
            "password": password
        }
        self.assertSchemaPost(url, "$signUpRequest", "$signUpResponse", data, None)
        user = User.objects.filter(username="tester")
        self.assertEqual(user.count(), 1)

        # Password gets hashed
        self.assertTrue(user[0].check_password("testtest"))

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

    def test_user_can_change_password(self):
        felicia = UserFactory(username='felicia')
        felicia.set_password('password')
        felicia.save()
        stranger = UserFactory()
        url = reverse("users-password", args=[felicia.pk])

        data = {
            "old_password": base64.encodestring("password"),
            "password": base64.encodestring("felicia")
        }
        # Unauthenticated user can't change password
        self.assertSchemaPatch(url, "$changePasswordRequest", "$changePasswordResponse", data, None, unauthorized=True)
        self.assertFalse(User.objects.get(pk=felicia.pk).check_password("felicia"))

        # Stranger can't change another user's password
        self.assertSchemaPatch(url, "$changePasswordRequest", "$changePasswordResponse", data, stranger,
                               unauthorized=True)
        self.assertFalse(User.objects.get(pk=felicia.pk).check_password("felicia"))

        # User can change their own password
        self.assertSchemaPatch(url, "$changePasswordRequest", "$changePasswordResponse", data, felicia)
        self.assertTrue(User.objects.get(pk=felicia.pk).check_password("felicia"))

    def test_user_can_get_token(self):
        """
        Below is the test I want. But it fails because django-oauth-toolkit will only accept requests with
        content-type application/x-www-form-urlencoded. DRF does not appear to support this type.

        url = reverse("oauth2_provider:token")
        data = {
            "username": self.user.username,
            "email": self.user.email,
            "client_id": self.user.application_set.first().client_id,
            "client_secret": self.user.application_set.first().client_secret,
            "grant_type": "password"
        }
        self.assertManticomPOSTResponse(url, "$tokenRequest", "$tokenResponse", data, None)
        """
        pass

    def test_token_authenticates_user(self):
        pass
