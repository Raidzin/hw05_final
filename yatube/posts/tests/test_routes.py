from django.test import TestCase
from django.urls import reverse

ID = 5
USERNAME = 'testuserauthor'
SLUG = 'test1'


class RouteTests(TestCase):

    def test_routes(self):
        cases = [
            ['/', 'main', None],
            ['/create/', 'post_create', None],
            ['/follow/', 'follow_index', None],
            [f'/profile/{USERNAME}/', 'profile', {'username': USERNAME}],
            [f'/group/{SLUG}/', 'group_posts', {'slug': SLUG}],
            [f'/posts/{ID}/', 'post_detail', {'post_id': ID}],
            [f'/posts/{ID}/edit/', 'post_edit', {'post_id': ID}],
            [f'/posts/{ID}/comment/', 'add_comment', {'post_id': ID}],
        ]

        for url, name, kwargs in cases:
            with self.subTest(url=url):
                reverse_url = reverse(f'posts:{name}', kwargs=kwargs)
                self.assertEqual(url, reverse_url)
