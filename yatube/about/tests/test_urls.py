from django.test import TestCase, Client


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_static_urls(self):
        test_urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for test_url in test_urls:
            with self.subTest(test_url=test_url):
                response = self.guest_client.get(test_url)
                self.assertEqual(response.status_code, 200,
                                 f'ошибка доступа к {test_url}')
