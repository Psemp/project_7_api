from django.test import TestCase
from django.urls import reverse


class IndexPageTestCase(TestCase):

    # test that index returns a 200
    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)


class ContactPageTestCase(TestCase):

    # test that contact returns a 200
    def test_contact_page(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)


class AboutTestCase(TestCase):

    # test that about returns a 200
    def test_about_page(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
