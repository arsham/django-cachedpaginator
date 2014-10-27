from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django_cachedpaginator.utils import Paginator, PageNotAnInteger, EmptyPage, Page


class UtilsTestCase(TestCase):

    def setUp(self):
        for n in range(300):
            User.objects.create(username='number_%d' % n)

    def tearDown(self):
        User.objects.all().delete()

    def testPaginatorCreation(self):
        paginator = Paginator(User.objects.all(), 10, 'test_name', cache_timeout=666, count_timeout=666)
        self.assertIsInstance(paginator, Paginator)
        self.assertIsInstance(paginator.page(1), Page)
        self.assertEquals(paginator.cache_timeout, paginator.count_timeout)
        self.assertEquals(paginator.cache_timeout, 666)

    def testQueryPaginator(self):
        paginator = Paginator(User.objects.all(), 10, 'test_name')
        self.assertEquals(paginator.count, 300)
        self.assertRaises(EmptyPage, paginator.page, 99999)
        self.assertRaises(PageNotAnInteger, paginator.page, 'aaaa')
        self.assertIsInstance(paginator.page(1)[0], User)

    def testCacheKey(self):
        paginator = Paginator(User.objects.all(), 10, 'test_name', cache_timeout=666, count_timeout=777)
        self.assertIsInstance(paginator.build_cache_key(1), str)
        self.assertIn('test_name', paginator.build_cache_key(1))
        self.assertIn('666', paginator.build_cache_key(1))
        self.assertIn('777', paginator.build_cache_key(1))
        self.assertIn('10', paginator.build_cache_key(1))


class IntegrationTestCase(TestCase):

    def setUp(self):
        self.c = Client()
        for n in range(300):
            User.objects.create(username='number_%d' % n)

    def tearDown(self):
        User.objects.all().delete()

    def testCreatingFirstPage(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'test.html')
        self.assertIn('Total 300 Objects', str(response.content))
        self.assertNotIn('First', str(response.content))
        self.assertIn('Next', str(response.content))
        self.assertNotIn('Prev', str(response.content))
        self.assertIn('Last', str(response.content))
        self.assertIn('?page=1', str(response.content))

    def testCreatingMiddlePage(self):
        response = self.c.get('/?page=5')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'test.html')
        self.assertIn('Total 300 Objects', str(response.content))
        self.assertIn('First', str(response.content))
        self.assertIn('Prev', str(response.content))
        self.assertIn('Next', str(response.content))
        self.assertIn('Last', str(response.content))

    def testCreatingLastPage(self):
        response = self.c.get('/?page=30')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'test.html')
        self.assertIn('Total 300 Objects', str(response.content))
        self.assertIn('First', str(response.content))
        self.assertIn('Prev', str(response.content))
        self.assertNotIn('Next', str(response.content))
        self.assertNotIn('Last', str(response.content))
