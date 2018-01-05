from rest_framework.reverse import reverse
from test_project.test_app.models import Post
from test_project.test_app.tests.factories import UserFactory
from yak.rest_core.test import SchemaTestCase


class PermissionsTests(SchemaTestCase):
    def test_only_authed_user_can_create_post(self):
        """
        For default permission `IsOwnerOrReadOnly` verifies that any logged in user can create a post
        Non-authenticated users cannot create a post
        """
        url = reverse("posts-list")
        old_post_count = Post.objects.count()
        data = {
            "title": "i'm not logged in",
            "description": "so this shouldn't work"
        }
        self.assertSchemaPost(url, "$postRequest", "$postResponse", data, None, unauthorized=True)
        self.assertEqual(old_post_count, Post.objects.count())

        self.assertSchemaPost(url, "$postRequest", "$postResponse", data, UserFactory())
        self.assertEqual(old_post_count + 1, Post.objects.count())
