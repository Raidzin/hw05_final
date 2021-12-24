import re

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Post, User, Group

USERNAME = 'username'
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={
    'username': USERNAME})
LOGIN_URL = reverse('users:login')

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class FormsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.post = Post.objects.create(
            text='текст поста',
            author=cls.user)
        cls.group = Group.objects.create(
            title='название1',
            slug='group1',
            description='описание')
        cls.group_2 = Group.objects.create(
            title='название2',
            slug='group2',
            description='описание2')
        cls.POST_EDIT_URL = reverse('posts:post_edit', kwargs={
            'post_id': cls.post.id
        })
        cls.POST_COMMENT_URL = reverse('posts:add_comment', kwargs={
            'post_id': cls.post.id
        })
        cls.POST_DETAIL_URL = reverse('posts:post_detail', kwargs={
            'post_id': cls.post.id})
        cls.anonim = Client()
        cls.logined_user = Client()
        cls.logined_user.force_login(cls.user)

    def test_post_create(self):
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        post_data = {
            'text': 'текст поста нового',
            'group': self.group.id,
            'image': uploaded,
        }
        post_posts = set(Post.objects.all())
        response = self.logined_user.post(POST_CREATE_URL, data=post_data)
        post_posts = set(Post.objects.all()) - post_posts
        self.assertEqual(len(post_posts), 1)
        post = post_posts.pop()
        self.assertEqual(post.text, post_data['text'])
        self.assertEqual(post.group.id, post_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertRedirects(response, PROFILE_URL)
        self.assertTrue(re.match(str(post_data['image']).split('.')[0],
                                 str(post.image.file).split('/')[-1]))

    def test_comment_create(self):
        comment_data = {'text': 'текст комента'}
        comments = set(self.post.comments.all())
        response = self.logined_user.post(self.POST_COMMENT_URL,
                                          data=comment_data)
        comments = set(self.post.comments.all()) - comments
        self.assertEqual(len(comments), 1)
        comment = comments.pop()
        self.assertEqual(comment.text, comment_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_post_edit(self):
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        post_data = {
            'text': 'текст редактированного нового',
            'group': self.group_2.id,
            'image': uploaded,
        }
        response = self.logined_user.post(self.POST_EDIT_URL, data=post_data,
                                          follow=True)
        post = response.context.get('post')
        self.assertEqual(post.text, post_data['text'])
        self.assertEqual(post.group.id, post_data['group'])
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertTrue(re.match(str(post_data['image']).split('.')[0],
                                 str(post.image.file).split('/')[-1]))

    def test_forms_context(self):
        urls = [POST_CREATE_URL, self.POST_EDIT_URL]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.logined_user.get(url)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get('form').fields.get(
                            value)
                        self.assertIsInstance(form_field, expected)

    def test_anonim_create_post(self):
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        post_data = {
            'text': 'текст нового',
            'group': self.group_2.id,
            'image': uploaded,
        }
        posts = set(Post.objects.all())
        self.anonim.post(POST_CREATE_URL, data=post_data,
                         follow=True)
        posts = set(Post.objects.all()) - posts
        self.assertEqual(len(posts), 0)

    def test_anonim_edit_post(self):
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        post_data = {
            'text': 'текст нового',
            'group': self.group_2.id,
            'image': uploaded,
        }
        self.anonim.post(self.POST_EDIT_URL, data=post_data, follow=True)
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(self.post.text, post.text)
        self.assertEqual(self.post.group, post.group)
        self.assertEqual(self.post.author, post.author)

    def test_anonim_comment_create(self):
        comment_data = {'text': 'текст коммента'}
        comments = set(self.post.comments.all())
        self.anonim.post(self.POST_COMMENT_URL, data=comment_data)
        comments = set(self.post.comments.all()) - comments
        self.assertEqual(len(comments), 0)
