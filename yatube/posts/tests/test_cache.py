from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post


User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Test_name')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_text'
        )

    def setUp(self):
        self.guest_client = Client()

    def test_cache_2(self):
        """После удаление поста он остается на странице"""
        response = self.guest_client.get('')
        first_response = response.content
        CacheTests.post.delete()
        response = self.guest_client.get('')
        second_response = response.content
        self.assertEqual(
            first_response, second_response
        )
