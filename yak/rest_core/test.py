import json
from rest_framework.test import APITestCase
from django.conf import settings
from yak.settings import yak_settings
from django.test import TestCase
from flake8.engine import get_style_guide
import flake8.main
import sys


class APITestCaseWithAssertions(APITestCase):
    """
    Taken from Tastypie's tests to improve readability
    """
    def assertHttpOK(self, resp):
        """
        Ensures the response is returning a HTTP 200.
        """
        return self.assertEqual(resp.status_code, 200, resp)

    def assertHttpCreated(self, resp):
        """
        Ensures the response is returning a HTTP 201.
        """
        return self.assertEqual(resp.status_code, 201, resp)

    def assertHttpAccepted(self, resp):
        """
        Ensures the response is returning either a HTTP 202 or a HTTP 204.
        """
        return self.assertIn(resp.status_code, [202, 204], resp)

    def assertHttpMultipleChoices(self, resp):
        """
        Ensures the response is returning a HTTP 300.
        """
        return self.assertEqual(resp.status_code, 300, resp)

    def assertHttpSeeOther(self, resp):
        """
        Ensures the response is returning a HTTP 303.
        """
        return self.assertEqual(resp.status_code, 303, resp)

    def assertHttpNotModified(self, resp):
        """
        Ensures the response is returning a HTTP 304.
        """
        return self.assertEqual(resp.status_code, 304, resp)

    def assertHttpBadRequest(self, resp):
        """
        Ensures the response is returning a HTTP 400.
        """
        return self.assertEqual(resp.status_code, 400, resp)

    def assertHttpUnauthorized(self, resp):
        """
        Ensures the response is returning a HTTP 401.
        """
        return self.assertEqual(resp.status_code, 401, resp)

    def assertHttpForbidden(self, resp):
        """
        Ensures the response is returning a HTTP 403.
        """
        return self.assertEqual(resp.status_code, 403, resp)

    def assertHttpNotFound(self, resp):
        """
        Ensures the response is returning a HTTP 404.
        """
        return self.assertEqual(resp.status_code, 404, resp)

    def assertHttpMethodNotAllowed(self, resp):
        """
        Ensures the response is returning a HTTP 405.
        """
        return self.assertEqual(resp.status_code, 405, resp)

    def assertHttpNotAllowed(self, resp):
        """
        Depending on how we purposefully reject a call (e.g., limiting
        methods, using permission classes, etc.), we may have a few different
        HTTP response codes. Bundling these together into a single assertion
        so that schema tests can be more flexible.
        """
        return self.assertIn(resp.status_code, [401, 403, 404, 405], resp)

    def assertHttpConflict(self, resp):
        """
        Ensures the response is returning a HTTP 409.
        """
        return self.assertEqual(resp.status_code, 409, resp)

    def assertHttpGone(self, resp):
        """
        Ensures the response is returning a HTTP 410.
        """
        return self.assertEqual(resp.status_code, 410, resp)

    def assertHttpUnprocessableEntity(self, resp):
        """
        Ensures the response is returning a HTTP 422.
        """
        return self.assertEqual(resp.status_code, 422, resp)

    def assertHttpTooManyRequests(self, resp):
        """
        Ensures the response is returning a HTTP 429.
        """
        return self.assertEqual(resp.status_code, 429, resp)

    def assertHttpApplicationError(self, resp):
        """
        Ensures the response is returning a HTTP 500.
        """
        return self.assertEqual(resp.status_code, 500, resp)

    def assertHttpNotImplemented(self, resp):
        """
        Ensures the response is returning a HTTP 501.
        """
        return self.assertEqual(resp.status_code, 501, resp)

    def assertValidJSONResponse(self, resp):
        """
        Given a ``HttpResponse`` coming back from using the ``client``, assert that
        you get back:

        * An HTTP 200
        * The correct content-type (``application/json``)
        """
        self.assertHttpOK(resp)
        self.assertTrue(resp['Content-Type'].startswith('application/json'))


class SchemaTestCase(APITestCaseWithAssertions):
    def setUp(self):
        super(SchemaTestCase, self).setUp()

        # Parse schema objects for use later
        self.schema_objects = {}
        with open(yak_settings.API_SCHEMA) as file:
            schema_data = json.loads(file.read())
            for schema_obj in schema_data["objects"]:
                self.schema_objects.update(schema_obj)

    def check_schema_keys(self, data_object, schema_fields):
        """
        `data_object` is the actual JSON being sent or received
        `schema_fields` is the expected JSON based on the schema file
        """
        required_fields = []

        for schema_field, schema_type in schema_fields.iteritems():
            # If this field is actually another related object, then check that object's fields as well
            schema_parts = schema_type.split(',')
            is_list = False
            is_optional = False
            new_schema_object = None
            for part in schema_parts:
                # Parse through all parts, regardless of ordering
                if part in ["array", "O2M", "M2M"]:
                    is_list = True
                elif part == "optional":
                    is_optional = True
                elif part.startswith('$'):
                    new_schema_object = part

            if not is_optional:
                required_fields.append(schema_field)

            if new_schema_object:
                if schema_field not in data_object or data_object[schema_field] is None:
                    # If our new object to check is None and optional then continue, else raise an error
                    if is_optional:
                        continue
                    else:
                        raise self.failureException("No data for object {0}".format(new_schema_object))

                new_data_object = data_object[schema_field]
                if is_list:
                    # If our new object to check is a list of these objects, continue if we don't have any data
                    # Else grab the first one in the list
                    if len(new_data_object) == 0:
                        continue
                    new_data_object = new_data_object[0]

                self.check_schema_keys(new_data_object, self.schema_objects[new_schema_object])

        set_required_fields = set(required_fields)
        set_data_object = set(data_object)
        set_schema_fields = set(schema_fields)
        # The actual `data_object` contains every required field
        self.assertTrue(set_required_fields.issubset(set_data_object),
                        "Data did not match schema.\nMissing fields: {}".format(
                            set_required_fields.difference(set_data_object)))

        # The actual `data_object` contains no extraneous fields not found in the schema
        self.assertTrue(set_data_object.issubset(set_schema_fields),
                        "Data did not match schema.\nExtra fields: {}".format(
                            set_data_object.difference(set_schema_fields)))

    def add_credentials(self, user):
        """
        Adds OAuth2.0 authentication as specified in `rest_user`
        If no user is specified, clear any existing credentials (allows us to
        check unauthorized requests)
        """
        if user:
            token = user.accesstoken_set.first()
            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.token)
        else:
            self.client.credentials()

    def check_response_data(self, response, response_object_name):
        results_data = response.data

        if "results" in response.data or isinstance(response.data, list):  # If multiple objects returned
            if "results" in response.data:
                results_data = response.data["results"]
            else:  # A plain list is returned, i.e. from a bulk update request
                results_data = response.data

            if len(results_data) == 0:
                raise self.failureException("No data to compare response")
            results_data = results_data[0]

        self.check_schema_keys(results_data, self.schema_objects[response_object_name])

    def assertSchemaGet(
            self,
            url,
            parameters,
            response_object_name,
            user,
            unauthorized=False):
        """
        Checks GET parameters and results match the schema
        """
        self.add_credentials(user)
        response = self.client.get(url, parameters)
        if unauthorized:
            self.assertHttpNotAllowed(response)
        else:
            self.assertValidJSONResponse(response)
            self.check_response_data(response, response_object_name)

        return response

    def assertSchemaPost(
            self,
            url,
            request_object_name,
            response_object_name,
            data,
            user,
            format="json",
            unauthorized=False,
            status_OK=False):
        """
        Checks POST data and results match schema

        status_OK: used for non-standard POST requests that do not return 201,
            e.g. if creating a custom route that uses POST
        """
        if isinstance(data, list):  # Check first object if this is a bulk create
            self.check_schema_keys(data[0], self.schema_objects[request_object_name])
        else:
            self.check_schema_keys(data, self.schema_objects[request_object_name])

        self.add_credentials(user)
        response = self.client.post(url, data, format=format)
        if unauthorized:
            self.assertHttpNotAllowed(response)
        elif status_OK:
            self.assertHttpOK(response)
            self.assertTrue(response['Content-Type'].startswith('application/json'))
            self.check_response_data(response, response_object_name)
        else:
            self.assertHttpCreated(response)
            self.assertTrue(response['Content-Type'].startswith('application/json'))
            self.check_response_data(response, response_object_name)

        return response

    def assertSchemaPatch(
            self,
            url,
            request_object_name,
            response_object_name,
            data,
            user,
            format="json",
            unauthorized=False):
        """
        Checks PATCH data and results match schema
        """
        self.check_schema_keys(data, self.schema_objects[request_object_name])

        self.add_credentials(user)
        response = self.client.patch(url, data, format=format)
        if unauthorized:
            self.assertHttpNotAllowed(response)
        else:
            self.assertValidJSONResponse(response)
            self.check_response_data(response, response_object_name)

        return response

    def assertSchemaPut(
            self,
            url,
            request_object_name,
            response_object_name,
            data,
            user,
            format="json",
            unauthorized=False,
            forbidden=False):
        """
        Assumes PUT is used for bulk updates, not single updates.
        Runs a PUT request and checks the PUT data and results match the
        schema for bulk updates. Assumes that all objects sent in a bulk
        update are identical, and hence only checks that the first one
        matches the schema.
        """
        self.check_schema_keys(data[0], self.schema_objects[request_object_name])

        self.add_credentials(user)
        response = self.client.put(url, data, format=format)
        if forbidden:
            # Attempting to update an object that isn't yours means it isn't in the queryset. DRF reads this as
            # creating, not updating. Since we have the `allow_add_remove` option set to False, creating isn't
            # allowed. So, instead of being rejected with a 403, server returns a 400 Bad Request.
            self.assertHttpBadRequest(response)
        elif unauthorized:
            self.assertHttpUnauthorized(response)
        else:
            self.assertValidJSONResponse(response)
            self.check_response_data(response, response_object_name)

        return response

    def assertSchemaDelete(
            self,
            url,
            user,
            unauthorized=False):
        """
        Checks DELETE
        """
        self.add_credentials(user)
        response = self.client.delete(url)

        if unauthorized:
            self.assertHttpNotAllowed(response)
        else:
            self.assertHttpAccepted(response)

        return response

    def assertPhotoUpload(self):
        pass

    def assertVideoUpload(
            self,
            url,
            obj_to_update,
            user,
            path_to_video,
            path_to_thumbnail,
            related_media_model=None,
            related_name=None,
            unauthorized=False
    ):
        """
        Checks that the video is uploaded and saved
        If the model being 'updated' is not the model that actually stores
        files (e.g., there is a Media model that has a relation to the model
        being updated), pass that model and the keyword field on that model
        that relates to the model being updated
        """
        self.add_credentials(user)
        kwargs = {
            "data": {
                'video_file': open(settings.PROJECT_ROOT + path_to_video, 'rb')
            },
            'format': 'multipart'
        }
        response = self.client.post(url, **kwargs)

        if unauthorized:
            self.assertHttpForbidden(response)
        else:
            self.assertHttpCreated(response)
            self.assertTrue(response['Content-Type'].startswith('application/json'))

            # Check the video and thumbnail are saved
            if related_media_model and related_name:
                filters = {
                    related_name: obj_to_update
                }
                obj_to_update = related_media_model.objects.filter(**filters)[0]
            else:
                obj_to_update = obj_to_update.__class__.objects.get(pk=obj_to_update.pk)
            original_file_field_name = getattr(obj_to_update, "original_file_name", "original_file")
            original_file = getattr(obj_to_update, original_file_field_name)
            self.assertEqual(
                original_file.file.read(),
                open(settings.PROJECT_ROOT + path_to_video, 'r').read()
            )
            self.assertEqual(
                obj_to_update.thumbnail.file.read(),
                open(settings.PROJECT_ROOT + path_to_thumbnail, 'r').read()
            )


class YAKSyntaxTest(TestCase):
    def check_syntax(self):
        """
        From flake8
        """
        packages = settings.PACKAGES_TO_TEST

        # Prepare
        config_file = getattr(settings, 'FLAKE8_CONFIG', flake8.main.DEFAULT_CONFIG)
        flake8_style = get_style_guide(parse_argv=True, config_file=config_file)
        options = flake8_style.options

        if options.install_hook:
            from flake8.hooks import install_hook
            install_hook()

        # Save to file for later printing instead of printing now
        old_stdout = sys.stdout
        sys.stdout = out = open('syntax_output', 'w+')

        # Run the checkers
        report = flake8_style.check_files(paths=packages)

        sys.stdout = old_stdout

        # Print the final report
        options = flake8_style.options
        if options.statistics:
            report.print_statistics()
        if options.benchmark:
            report.print_benchmark()
        if report.total_errors:
            out.close()
            with open("syntax_output") as f:
                self.fail("{0} Syntax warnings!\n\n{1}".format(report.total_errors, f.read()))
