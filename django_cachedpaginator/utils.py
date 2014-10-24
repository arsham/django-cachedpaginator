
from django.core.cache import cache
from django.core.paginator import Paginator as DjangoPaginator, Page, EmptyPage, PageNotAnInteger


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

        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
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
            page = super().page(number)
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
                _total = super().count
                cache.set(key, _total, self.count_timeout)
            self._cached_num_objects = _total

        return self._cached_num_objects


class CachedPaginatorViewMixin:

    """
    A Class Based View Mixin to use cached paginator instead of django's stock one
    """
    paginator_class = Paginator
    paginate_by = 10

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs):

        assert hasattr(self, "get_cache_key"), 'You should implement get_cache_key in your view'
        cache_timeout = getattr(self, 'cache_timeout', 60)
        count_timeout = getattr(self, 'count_timeout', 3600)

        return self.paginator_class(
            queryset, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page,
            cache_key=self.get_cache_key(),
            cache_timeout=cache_timeout,
            count_timeout=count_timeout,
            **kwargs)
