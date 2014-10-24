from django import template
from django.conf import settings
from django.core.paginator import Page

register = template.Library()

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


@register.inclusion_tag(PAGINATOR_TEMPLATE, takes_context=True, name='paginate')
def paginate(context, object_list):
    """
    Creates a paginator element and draws it based on the template
    @type object_list: django.core.paginator.Page
    """
    assert isinstance(object_list, Page), 'object_list should be a Page of Paginator object'
    query_string = context['request'].GET.copy()

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
