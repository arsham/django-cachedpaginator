import six
import abc
from django.core.cache import cache
from django.conf import settings
from django.core.paginator import Paginator as DjangoPaginator, Page, EmptyPage, PageNotAnInteger


PAGINATOR_TOTAL_PAGES = getattr(settings, 'PAGINATOR_TOTAL_PAGES', 10)
PAGINATOR_TEMPLATE = getattr(settings, 'PAGINATOR_TEMPLATE', 'django_cachedpaginator/paginator_template.html')
PAGINATOR_ID_PREFIX = getattr(settings, 'PAGINATOR_ID_PREFIX', 'paginator_page')
PAGINATOR_FIRST_CLASS = getattr(settings, 'PAGINATOR_FIRST_CLASS', 'first')
PAGINATOR_FIRST_VERBOSE = getattr(settings, 'PAGINATOR_FIRST_VERBOSE', 'First')
PAGINATOR_PREVIOUS_CLASS = getattr(settings, 'PAGINATOR_PREVIOUS_CLASS', 'previous')
PAGINATOR_PREVIOUS_VERBOSE = getattr(settings, 'PAGINATOR_PREVIOUS_VERBOSE', 'Previous')
PAGINATOR_NEXT_CLASS = getattr(settings, 'PAGINATOR_NEXT_CLASS', 'next')
PAGINATOR_NEXT_VERBOSE = getattr(settings, 'PAGINATOR_NEXT_VERBOSE', 'Next')
PAGINATOR_LAST_CLASS = getattr(settings, 'PAGINATOR_LAST_CLASS', 'last')
PAGINATOR_LAST_VERBOSE = getattr(settings, 'PAGINATOR_LAST_VERBOSE', 'Last')
PAGINATOR_PAGE_PARAMETER = getattr(settings, 'PAGINATOR_PAGE_PARAMETER', 'page')


class Paginator(DjangoPaginator):

    """
    A paginator that caches the results and the total amount of object list on a page by page basis.

    Usage:
        cache_key = 'user_your_own_key'
        cache_timeout = 600 # 10 minutes
        count_timeout = 3600
        object_list = ExpensiveModel.objects.run_crazy_query()
        paginator = Paginator(object_list, 20, cache_key, cache_timeout, count_timeout)
        page = paginator.page(request.GET.get('page', 1))
        object_list = page.object_list

    """

    def __init__(self, object_list, per_page, cache_key, cache_timeout=300, count_timeout=600, orphans=0, allow_empty_first_page=True):

        super(Paginator, self).__init__(object_list, per_page, orphans, allow_empty_first_page)
        self.cache_key = cache_key.replace(' ', '_')
        self.cache_timeout = cache_timeout
        self._cached_num_pages = None
        self._cached_num_objects = None
        self.count_timeout = count_timeout or cache_timeout

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.

        This will attempt to pull the results out of the cache first, based on
        the number of objects per page and the requested page number. If not
        found in the cache, it will pull a fresh list and then cache that
        result.
        """
        number = self.validate_number(number)
        cached_object_list = cache.get(self.build_cache_key(number), None)

        if cached_object_list is not None:
            page = Page(cached_object_list, number, self)
        else:
            page = super(Paginator, self).page(number)
            # Since the results are fresh, cache it.
            cache.set(self.build_cache_key(number), page.object_list, self.cache_timeout)

        return page

    def build_cache_key(self, page_number):
        """Appends the relevant pagination bits to the cache key."""
        return "%s:%s:%s:%d:%d" % (self.cache_key, self.per_page, page_number, self.cache_timeout, self.count_timeout)

    def build_cache_key_total(self, key):
        """This one is used to cache the total number."""
        return "%s:%s:%d:%d" % (self.cache_key, key, self.cache_timeout, self.count_timeout)

    @property
    def count(self):
        """
        Returns the total number of objects, across all pages.
        This caches the results cache service and again caches it as a property because the called calls it several times
        """
        if self._cached_num_objects is None:
            key = self.build_cache_key_total('total_number')
            _total = cache.get(key, None)
            if not _total:
                _total = super(Paginator, self).count
                cache.set(key, _total, self.count_timeout)
            self._cached_num_objects = _total

        return self._cached_num_objects


@six.add_metaclass(abc.ABCMeta)
class CachedPaginatorViewMixin(object):

    """
    A Class Based View Mixin to use cached paginator instead of django's stock one
    """
    paginator_class = Paginator
    paginate_by = 10

    @abc.abstractmethod
    def get_cache_key(self):
        pass

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs):

        cache_timeout = getattr(self, 'cache_timeout', 60)
        count_timeout = getattr(self, 'count_timeout', 3600)

        return self.paginator_class(
            queryset, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page,
            cache_key=self.get_cache_key(),
            cache_timeout=cache_timeout,
            count_timeout=count_timeout,
            **kwargs)


def paginate_object_list(query_string, object_list):
    """
    Creates a paginator element and returns context information for use in included template
    @param query_string: a copy of query string
    @type object_list: django.core.paginator.Page
    """
    assert isinstance(object_list, Page), 'object_list should be a Page of Paginator object'

    paginator_list = []
    middle_page = int(PAGINATOR_TOTAL_PAGES / 2)
    current_page = object_list.number
    domain_min = max(1, current_page - middle_page + 1)
    domain_max = min(object_list.paginator.num_pages + 1, domain_min + PAGINATOR_TOTAL_PAGES)
    domain_min = max(1, min(domain_min, object_list.paginator.num_pages - PAGINATOR_TOTAL_PAGES + 1))

    if current_page > 1:
        query_string[PAGINATOR_PAGE_PARAMETER] = 1
        paginator_list.append({
            'verbose_name': PAGINATOR_FIRST_VERBOSE,
            'page': 1,
            'class': PAGINATOR_FIRST_CLASS,
            'id': '%s_first' % PAGINATOR_ID_PREFIX,
            'link': query_string.urlencode(),
        })
        query_string[PAGINATOR_PAGE_PARAMETER] = current_page - 1

        paginator_list.append({
            'verbose_name':  PAGINATOR_PREVIOUS_VERBOSE,
            'page': current_page - 1,
            'class':  PAGINATOR_PREVIOUS_CLASS,
            'id': '%s_prev' % PAGINATOR_ID_PREFIX,
            'link': query_string.urlencode(),
        })

    for i in range(domain_min, domain_max):
        query_string[PAGINATOR_PAGE_PARAMETER] = i
        paginator_list.append(
            {
                'verbose_name': i,
                'page': i,
                'class': 'active' if i == current_page else '',
                'id': '%s_%d' % (PAGINATOR_ID_PREFIX, i),
                'link': query_string.urlencode(),
            }
        )

    if domain_max < object_list.paginator.num_pages + 1:

        query_string[PAGINATOR_PAGE_PARAMETER] = current_page + 1
        paginator_list.append({
            'verbose_name': PAGINATOR_NEXT_VERBOSE,
            'page': current_page + 1,
            'class': PAGINATOR_NEXT_CLASS,
            'id': '%s_next' % PAGINATOR_ID_PREFIX,
            'link': query_string.urlencode(),
        })

        query_string[PAGINATOR_PAGE_PARAMETER] = object_list.paginator.num_pages
        paginator_list.append({
            'verbose_name': PAGINATOR_LAST_VERBOSE,
            'page': object_list.paginator.num_pages,
            'class': PAGINATOR_LAST_CLASS,
            'id': '%s_last' % PAGINATOR_ID_PREFIX,
            'link': query_string.urlencode(),
        })

    return {'object_list': object_list, 'paginator_list': paginator_list}
