from django.views.generic import ListView
from django_cachedpaginator import CachedPaginatorMixin


class TestView(CachedPaginatorMixin, ListView):

    pass
