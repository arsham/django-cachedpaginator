django-cachedpaginator
============

# About

A paginator that caches pages and result count. Very handy when you need to paginate an expensive query

This application was inspired by https://djangosnippets.org/snippets/1173/

## Usage

### View

In your view:

```python
from django_cachedpaginator import Paginator, PageNotAnInteger, EmptyPage


def my_view(request):
    cache_key = 'user_your_own_key'
    cache_timeout = 600 # 10 minutes
    count_timeout = 3600
    page = request.GET.get('page')

    object_list = ExpensiveModel.objects.all()
    paginator = Paginator(object_list, 20, cache_key, cache_timeout, count_timeout)

    try:
        object_list = object_list.page(page)
    except PageNotAnInteger:
        object_list = object_list.page(1)
    except EmptyPage:
        object_list = object_list.page(image_list.num_pages)
```

Or in you CBV view:

```python
from django_cachedpaginator import CachedPaginatorViewMixin


class MyView(CachedPaginatorViewMixin, ListView):

    ....
    paginate_by = 7
    cache_timeout = 60
    cache_key = "my_view"
```

And it will automatically caches the pagination.


## Templates

IMPORTANT: Make sure you add 'django_cachedpaginator' to your INSTALLLED_APPS settings, otherwide django cannot load the tag
All you need to do is to load the tags and pass your object_list to paginator tag like so:

```twig
{% load cached_paginator %}

...

{% paginate object_list %}
```

If you want to override the template that is used to render the paginator, you have a couple of options:
* Either create a file in your template folder (the one you've set in your settings file) by this name: django_cachedpaginator/paginator_template.html
* or set this variable in your settings file: PAGINATOR_TEMPLATE = 'path/to/your/template'

# Settings

You can set any of these in your settings file if you needed to:

PAGINATOR_TOTAL_PAGES

    default: 10

PAGINATOR_TEMPLATE

    default: 'django_cachedpaginator/paginator_template.html'

PAGINATOR_ID_PREFIX

    default: 'paginator_page'
    purpose: element's id prefix in your output

PAGINATOR_FIRST_CLASS

    default: 'first'
    purpose: element's class in your output

PAGINATOR_FIRST_VERBOSE

    default: 'First'
    purpose: String to show.

PAGINATOR_PREVIOUS_CLASS

    default: 'previous'

PAGINATOR_PREVIOUS_VERBOSE

    default: 'Previous'

PAGINATOR_NEXT_CLASS

    default: 'next'

PAGINATOR_NEXT_VERBOSE

    default: 'Next'

PAGINATOR_LAST_CLASS

    default: 'last'

PAGINATOR_LAST_VERBOSE

    default: 'Last'

PAGINATOR_PAGE_PARAMETER

    default: 'page'
    purpose: name of the parameter in your query string

# Notes

cache_timeout nad count_timeout are measured in seconds and are optional. Defaults are 300 and 600.

There is no need to add the page in cache_key because Paginator takes care of it. Actually here is a list of variables added to key:

* cache_key
* per_page
* page_number
* cache_timeout
* count_timeout

Therefore when you change any of these, your previous cache expires.
