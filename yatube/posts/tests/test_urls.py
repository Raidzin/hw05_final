from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

USERNAME = 'testuserauthor'
SLUG = 'test1'

INDEX_URL = reverse('posts:main')
POST_CREATE_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
PROFILE_URL = reverse('posts:profile', kwargs={
    'username': USERNAME})
GROUP_POSTS_URL = reverse('posts:group_posts', kwargs={
    'slug': SLUG})


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
        cls.POST_COMMENT_URL = reverse('posts:add_comment', kwargs={
            'post_id': cls.post.id})

    def setUp(self):
        self.guest = Client()
        self.another = Client()
        self.author = Client()

        self.another.force_login(self.test_user)
        self.author.force_login(self.user_author)

    def test_templates(self):
        posts_templates = {
            INDEX_URL: 'posts/index.html',
            GROUP_POSTS_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            POST_CREATE_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
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
        ]

        for url, client, code in cases:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, code)

    def test_redirects(self):
        cases = [
            [POST_CREATE_URL, self.guest,
             f'{LOGIN_URL}?next={POST_CREATE_URL}'],
            [self.POST_EDIT_URL, self.guest,
             f'{LOGIN_URL}?next={self.POST_EDIT_URL}'],
            [self.POST_EDIT_URL, self.another, self.POST_DETAIL_URL],
            [self.POST_COMMENT_URL, self.another, self.POST_DETAIL_URL]
        ]

        for url, client, redirect in cases:
            with self.subTest(url=url, redirect=redirect):
                self.assertRedirects(client.get(url), redirect)
