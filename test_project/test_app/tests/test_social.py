from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.reverse import reverse

from test_project.test_app.models import Post
from test_project.test_app.tests.factories import UserFactory, PostFactory, CommentFactory
from yak.rest_core.test import SchemaTestCase
from yak.rest_social_network.models import Follow, Comment, Tag, Like

User = get_user_model()


class BaseAPITests(SchemaTestCase):
    def setUp(self):
        super(BaseAPITests, self).setUp()
        self.dev_user = UserFactory()


class FlagTestCase(BaseAPITests):
    def test_users_can_flag_content(self):
        test_user = UserFactory()
        content_type = ContentType.objects.get_for_model(Post)
        flag_url = reverse('flag')
        data = {
            'content_type': content_type.pk,
            'object_id': PostFactory().pk
        }
        self.assertSchemaPost(flag_url, "$flagRequest", "$flagResponse", data, test_user)


class ShareTestCase(BaseAPITests):
    def test_users_can_share_content(self):
        test_user = UserFactory()
        content_type = ContentType.objects.get_for_model(Post)
        shares_url = reverse('shares-list')
        data = {
            'content_type': content_type.pk,
            'object_id': PostFactory().pk,
            'shared_with': [test_user.pk]
        }
        self.assertSchemaPost(shares_url, "$shareRequest", "$shareResponse", data, self.dev_user)

    def test_users_can_share_content_multiple_times(self):
        sharing_user = UserFactory()
        test_user = UserFactory()
        content_type = ContentType.objects.get_for_model(Post)
        shares_url = reverse('shares-list')
        data = {
            'content_type': content_type.pk,
            'object_id': PostFactory().pk,
            'shared_with': [test_user.pk]
        }
        self.assertSchemaPost(shares_url, "$shareRequest", "$shareResponse", data, sharing_user)
        data['shared_with'] = [self.dev_user.pk]
        self.assertSchemaPost(shares_url, "$shareRequest", "$shareResponse", data, sharing_user)


class LikeTestCase(BaseAPITests):
    def test_users_can_like_content(self):
        content_type = ContentType.objects.get_for_model(Post)
        likes_url = reverse('likes-list')
        data = {
            'content_type': content_type.pk,
            'object_id': PostFactory().pk,
        }
        self.assertSchemaPost(likes_url, "$likeRequest", "$likeResponse", data, self.dev_user)

    def test_liked_mixin(self):
        post = PostFactory()
        url = reverse("posts-detail", args=[post.pk])
        like = Like.objects.create(content_type=ContentType.objects.get_for_model(Post), object_id=post.pk,
                                   user=self.dev_user)
        response = self.assertSchemaGet(url, None, "$postResponse", self.dev_user)
        self.assertEqual(response.data["liked_id"], like.pk)

        other_post = PostFactory()
        url = reverse("posts-detail", args=[other_post.pk])
        response = self.assertSchemaGet(url, None, "$postResponse", self.dev_user)
        self.assertIsNone(response.data["liked_id"])


class CommentTestCase(BaseAPITests):
    def test_users_can_comment_on_content(self):
        content_type = ContentType.objects.get_for_model(Post)
        comments_url = reverse('comments-list')
        data = {
            'content_type': content_type.pk,
            'object_id': PostFactory().pk,
            'description': 'This is a user comment.'
        }
        self.assertSchemaPost(comments_url, "$commentRequest", "$commentResponse", data, self.dev_user)

    def test_comment_related_tags(self):
        content_type = ContentType.objects.get_for_model(Post)
        Comment.objects.create(content_type=content_type,
                               object_id=1,
                               description='Testing of a hashtag. #django',
                               user=self.dev_user)
        tags_url = reverse('tags-list')
        response = self.assertSchemaGet(tags_url, None, "$tagResponse", self.dev_user)
        self.assertEqual(response.data['results'][0]['name'], 'django')
        self.assertIsNotNone(Tag.objects.get(name='django'))

    def test_comments_for_specific_object(self):
        test_user = UserFactory()
        post_content_type = ContentType.objects.get_for_model(Post)

        post = PostFactory(user=test_user)
        comment = CommentFactory(content_type=post_content_type, object_id=post.pk)

        post2 = PostFactory(user=test_user)
        CommentFactory(content_type=post_content_type, object_id=post2.pk)

        url = reverse('comments-list')
        parameters = {
            'content_type': post_content_type.pk,
            'object_id': post.pk,
        }
        response = self.assertSchemaGet(url, parameters, "$commentResponse", self.dev_user)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], comment.pk)


class UserFollowingTestCase(BaseAPITests):
    def test_user_can_follow_each_other(self):
        test_user1 = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)
        follow_url = reverse('follows-list')
        # Dev User to follow Test User 1
        data = {
            'content_type': user_content_type.pk,
            'object_id': test_user1.pk
        }
        response = self.assertSchemaPost(follow_url, "$followRequest", "$followResponse", data, self.dev_user)
        self.assertEqual(response.data['following']['username'], test_user1.username)

    def test_following_endpoint(self):
        test_user1 = UserFactory()
        test_user2 = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)
        # Dev User to follow User 1, User 2 to follow Dev User
        Follow.objects.create(content_type=user_content_type, object_id=test_user1.pk, user=self.dev_user)
        Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=test_user2)
        following_url = reverse('users-following', args=[self.dev_user.pk])
        response = self.assertSchemaGet(following_url, None, "$followResponse", self.dev_user)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['following']['username'], test_user1.username)

    def test_follower_endpoint(self):
        test_user1 = UserFactory()
        test_user2 = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)
        # Dev User to follow User 1, User 2 to follow Dev User
        Follow.objects.create(content_type=user_content_type, object_id=test_user1.pk, user=self.dev_user)
        Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=test_user2)
        followers_url = reverse('users-followers', args=[self.dev_user.pk])
        response = self.assertSchemaGet(followers_url, None, "$followResponse", self.dev_user)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['follower']['username'], test_user2.username)

    def test_follow_pagination(self):
        user_content_type = ContentType.objects.get_for_model(User)
        for _ in range(0, 30):
            user = UserFactory()
            Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=user)

        followers_url = reverse('users-followers', args=[self.dev_user.pk])
        response = self.assertSchemaGet(followers_url, None, "$followResponse", self.dev_user)
        self.assertEqual(len(response.data), settings.REST_FRAMEWORK['PAGE_SIZE'])
        response = self.assertSchemaGet(followers_url, {"page": 2}, "$followResponse", self.dev_user)
        self.assertEqual(len(response.data), 30 - settings.REST_FRAMEWORK['PAGE_SIZE'])

    def test_user_can_unfollow_user(self):
        follower = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)
        follow_object = Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=follower)
        follows_url = reverse('follows-detail', kwargs={'pk': follow_object.pk})

        # If you are not the follower of the user, you cannot unfollow the user
        self.assertSchemaDelete(follows_url, self.dev_user, unauthorized=True)

        # If you are the follower of that user, you can unfollow the user
        self.assertSchemaDelete(follows_url, follower)

        # Check that original follow object no longer exists
        self.assertEqual(Follow.objects.filter(pk=follow_object.pk).exists(), False)

    def test_user_following_and_follower_count(self):
        follower1 = UserFactory()
        follower2 = UserFactory()
        following = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)

        # Follower setup
        Follow.objects.create(content_type=user_content_type, object_id=following.pk, user=self.dev_user)
        Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=follower1)
        Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=follower2)

        users_url = reverse('users-detail', kwargs={'pk': self.dev_user.pk})
        response = self.assertSchemaGet(users_url, None, "$userResponse", self.dev_user)
        self.assertEqual(response.data['user_following_count'], 1)
        self.assertEqual(response.data['user_followers_count'], 2)

    def test_bulk_follow(self):
        user1 = UserFactory()
        user2 = UserFactory()

        url = reverse('follows-bulk-create')
        user_content_type = ContentType.objects.get_for_model(User)
        data = [
            {'content_type': user_content_type.pk, 'object_id': user1.pk},
            {'content_type': user_content_type.pk, 'object_id': user2.pk}
        ]
        self.assertSchemaPost(url, "$followRequest", "$followResponse", data, self.dev_user)
        self.assertEqual(user1.user_followers_count(), 1)
        self.assertEqual(user2.user_followers_count(), 1)

    def test_follow_id(self):
        follower = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)
        follow_object = Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=follower)
        url = reverse("users-detail", args=[self.dev_user.pk])
        response = self.assertSchemaGet(url, None, "$userResponse", follower)
        self.assertEqual(response.data['follow_id'], follow_object.pk)

        not_follower = UserFactory()
        url = reverse("users-detail", args=[self.dev_user.pk])
        response = self.assertSchemaGet(url, None, "$userResponse", not_follower)
        self.assertIsNone(response.data['follow_id'])
