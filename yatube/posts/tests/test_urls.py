from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

USERNAME = 'testuserauthor'
SLUG = 'test1'

INDEX_URL = reverse('posts:main')
POST_CREATE_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
GROUP_POSTS_URL = reverse('posts:group_posts', kwargs={'slug': SLUG})
FOLLOW_URL = reverse('posts:follow_index')
FOLLOW_AUTHOR_URL = reverse('posts:profile_follow',
                            kwargs={'username': USERNAME})
UNFOLLOW_AUTHOR_URL = reverse('posts:profile_unfollow',
                              kwargs={'username': USERNAME})


class URLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='тестовое название',
            slug=SLUG,
            description='тестовое описание')
        cls.group_2 = Group.objects.create(
            title='тестовое название 2',
            slug='test2',
            description='тестовое описаниe 2')
        cls.test_user = User.objects.create(
            username='testuser')
        cls.user_author = User.objects.create(
            username=USERNAME)
        cls.post = Post.objects.create(
            text='тестовый текст',
            author=cls.user_author)
        cls.post_2 = Post.objects.create(
            text='тестовый текст 2',
            author=cls.user_author,
            group=cls.group)

        cls.POST_DETAIL_URL = reverse('posts:post_detail', kwargs={
            'post_id': cls.post.id})
        cls.POST_EDIT_URL = reverse('posts:post_edit', kwargs={
            'post_id': cls.post.id})

        cls.guest = Client()
        cls.another = Client()
        cls.author = Client()

        cls.another.force_login(cls.test_user)
        cls.author.force_login(cls.user_author)

    def setUp(self):
        cache.clear()

    def test_templates(self):
        posts_templates = {
            INDEX_URL: 'posts/index.html',
            GROUP_POSTS_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            POST_CREATE_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            FOLLOW_URL: 'posts/follow.html',
        }

        for url, template in posts_templates.items():
            with self.subTest(route_name=url, temp=template):
                self.assertTemplateUsed(
                    self.author.get(url), template)

    def test_codes(self):
        cases = [
            [INDEX_URL, self.guest, 200],
            [GROUP_POSTS_URL, self.guest, 200],
            [PROFILE_URL, self.guest, 200],
            [self.POST_DETAIL_URL, self.guest, 200],
            [POST_CREATE_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.guest, 302],
            [POST_CREATE_URL, self.another, 200],
            [self.POST_EDIT_URL, self.another, 302],
            [self.POST_EDIT_URL, self.author, 200],
            [FOLLOW_URL, self.guest, 302],
            [FOLLOW_URL, self.another, 200],
            [FOLLOW_AUTHOR_URL, self.guest, 302],
            [FOLLOW_AUTHOR_URL, self.another, 302],
            [UNFOLLOW_AUTHOR_URL, self.guest, 302],
            [UNFOLLOW_AUTHOR_URL, self.another, 302],
            [FOLLOW_AUTHOR_URL, self.author, 302],
            [UNFOLLOW_AUTHOR_URL, self.author, 302],
        ]

        for url, client, code in cases:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, code)

    def test_redirects(self):
        cases = [
            [POST_CREATE_URL,
             self.guest,
             f'{LOGIN_URL}?next={POST_CREATE_URL}'],
            [self.POST_EDIT_URL,
             self.guest,
             f'{LOGIN_URL}?next={self.POST_EDIT_URL}'],
            [self.POST_EDIT_URL,
             self.another,
             self.POST_DETAIL_URL],
            [FOLLOW_URL,
             self.guest,
             f'{LOGIN_URL}?next={FOLLOW_URL}'],
            [FOLLOW_AUTHOR_URL,
             self.guest,
             f'{LOGIN_URL}?next={FOLLOW_AUTHOR_URL}'],
            [FOLLOW_AUTHOR_URL,
             self.another,
             PROFILE_URL],
            [UNFOLLOW_AUTHOR_URL,
             self.guest,
             f'{LOGIN_URL}?next={UNFOLLOW_AUTHOR_URL}'],
            [UNFOLLOW_AUTHOR_URL,
             self.another,
             PROFILE_URL],
            [FOLLOW_AUTHOR_URL,
             self.author,
             PROFILE_URL],
            [UNFOLLOW_AUTHOR_URL,
             self.author,
             PROFILE_URL],
        ]

        for url, client, redirect in cases:
            with self.subTest(url=url, redirect=redirect):
                self.assertRedirects(client.get(url), redirect)
