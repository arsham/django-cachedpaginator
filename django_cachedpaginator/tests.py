from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from django.forms import fields
from django.db.models import Q


class UtilsTestCase(TestCase):

    def testPopFields(self):
        pass


class IntegrationTestCase(TestCase):

    def setUp(self):

        self.c = Client()

    def testCreatingFormWidgetOnOutput(self):
        response = self.c.get('/?name=arsham&age=6&order_by=asc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         'django_cachedpaginator/test.html')

        form = response.context['search_bar']
        self.assertIn('<label for=', str(form))
        self.assertEqual(str(form).count('</option>'), 2)
