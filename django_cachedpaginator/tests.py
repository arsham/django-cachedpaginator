from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory


class UtilsTestCase(TestCase):

    def testPopFields(self):
        pass


class IntegrationTestCase(TestCase):

    def setUp(self):

        self.c = Client()

    def testCreatingFormWidgetOnOutput(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         'django_cachedpaginator/test.html')
