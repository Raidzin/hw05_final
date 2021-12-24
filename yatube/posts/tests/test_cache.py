from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, User

INDEX_URL = reverse('posts:main')


class TestCache(TestCase):

    def setUp(self):
        self.user_author = User.objects.create(
            username='USERNAME')
        self.post = Post.objects.create(
            text='тестовый текст',
            author=self.user_author)
        self.client = Client()

    def test_index_cache(self):
        content = self.client.get(INDEX_URL).content
        Post.objects.all().delete()
        self.assertEqual(content, Client().get(INDEX_URL).content)
        cache.clear()
        self.assertNotEqual(content, Client().get(INDEX_URL).content)
