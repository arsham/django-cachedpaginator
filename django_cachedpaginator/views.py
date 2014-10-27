from django.contrib.auth.models import User
from django.views.generic import ListView
from django_cachedpaginator.utils import CachedPaginatorViewMixin


class TestView(CachedPaginatorViewMixin, ListView):

    model = User
    template_name = 'test.html'
    paginate_by = 10

    def get_cache_key(self):
        return 'test'
