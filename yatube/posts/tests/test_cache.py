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

    def test_index_cache(self):
        content = Client().get(INDEX_URL).content
        Post.objects.create(
            text='новый тестовый текст',
            author=self.user_author)
        self.assertEqual(content, Client().get(INDEX_URL).content)
        cache.clear()
        self.assertNotEqual(content, Client().get(INDEX_URL).content)

