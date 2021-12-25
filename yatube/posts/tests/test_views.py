import shutil
import tempfile

from django.test import TestCase, Client
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse

from ..models import Post, Group, User, Follow
from ..views import POSTS_COUNT

USERNAME = 'testuserauthor'
SLUG = 'slug'
SLUG_2 = 'slug2'

INDEX_URL = reverse('posts:main')
FOLLOW_URL = reverse('posts:follow_index')
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
GROUP_POSTS_URL = reverse('posts:group_posts', kwargs={'slug': SLUG})
GROUP_POSTS_2_URL = reverse('posts:group_posts', kwargs={'slug': SLUG_2})
FOLLOW_USER_URL = reverse('posts:profile_follow',
                          kwargs={'username': USERNAME})
UNFOLLOW_USER_URL = reverse('posts:profile_unfollow',
                            kwargs={'username': USERNAME})

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostsViewTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='тестовое название',
            slug=SLUG,
            description='тестовое описание')
        cls.group_2 = Group.objects.create(
            title='тестовое название 2',
            slug=SLUG_2,
            description='тестовое описаниe 2')
        cls.test_user = User.objects.create(
            username='testuser')
        cls.user_author = User.objects.create(
            username=USERNAME)
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='тестовый текст',
            author=cls.user_author,
            group=cls.group,
            image=uploaded,
        )
        cls.follow = Follow.objects.create(
            author=cls.user_author,
            user=cls.test_user,
        )

        cls.POST_DETAIL_URL = reverse('posts:post_detail', kwargs={
            'post_id': cls.post.id})
        cls.POST_EDIT_URL = reverse('posts:post_edit', kwargs={
            'post_id': cls.post.id})

        cls.guest_client = Client()
        cls.logined_client = Client()
        cls.logined_client_author = Client()

        cls.logined_client.force_login(cls.test_user)
        cls.logined_client_author.force_login(cls.user_author)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_context(self):
        urls = [INDEX_URL,
                GROUP_POSTS_URL,
                PROFILE_URL,
                self.POST_DETAIL_URL,
                FOLLOW_URL,
                ]

        for url in urls:
            with self.subTest(url=url):
                response = self.logined_client.get(url)
                if 'page_obj' in response.context:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    post = response.context['page_obj'][0]
                else:
                    post = response.context['post']
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.id, self.post.id)
                self.assertEqual(post.image, self.post.image)

    def test_additional_context_profile(self):
        self.assertEqual(
            self.guest_client.get(PROFILE_URL).context['author'],
            self.user_author
        )

    def test_additional_context_group(self):
        response = self.guest_client.get(GROUP_POSTS_URL)
        group = response.context['group']
        self.assertEqual(group, self.group)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description,
                         self.group.description)

    def test_new_post_append_in_another_group(self):
        Follow.objects.all().delete()
        urls = [GROUP_POSTS_2_URL, FOLLOW_URL]
        for url in urls:
            with self.subTest(url=url):
                page_posts = self.logined_client.get(url).context['page_obj']
                self.assertNotIn(self.post, page_posts)


class PaginatorTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create(
            username=USERNAME
        )
        cls.group = Group.objects.create(
            title='тестовое название',
            slug=SLUG,
            description='тестовое описание')

        Post.objects.bulk_create(
            [Post(text=f'пост номер {i}', author=cls.user, group=cls.group)
             for i in range(POSTS_COUNT)]
        )
        cache.clear()

    def test_paginator(self):
        urls = [
            INDEX_URL,
            PROFILE_URL,
            GROUP_POSTS_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_COUNT)


class FollowsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create(
            username='user'
        )
        cls.client.force_login(cls.user)
        cls.author = User.objects.create(
            username=USERNAME
        )
        cls.client.get(FOLLOW_USER_URL)

    def test_follow_unfollow(self):
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )

    def test_unfollow(self):
        self.client.force_login(self.user)
        self.client.get(UNFOLLOW_USER_URL)
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )
