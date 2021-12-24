from django.test import TestCase
from django.urls import reverse

from posts.urls import app_name

ID = 5
USERNAME = 'testuserauthor'
SLUG = 'test1'


class RouteTests(TestCase):

    def test_routes(self):
        cases = [
            ['/', 'main', None],
            ['/create/', 'post_create', None],
            ['/follow/', 'follow_index', None],
            [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
            [f'/group/{SLUG}/', 'group_posts', [SLUG]],
            [f'/posts/{ID}/', 'post_detail', [ID]],
            [f'/posts/{ID}/edit/', 'post_edit', [ID]],
            [f'/posts/{ID}/comment/', 'add_comment', [ID]],
            [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
            [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]],
        ]

        for url, name, kwargs in cases:
            with self.subTest(url=url):
                reverse_url = reverse(f'{app_name}:{name}', args=kwargs)
                self.assertEqual(url, reverse_url)
