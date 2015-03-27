from django import template
from django_cachedpaginator.utils import PAGINATOR_TEMPLATE, paginate_object_list

__author__ = "Arsham Shirvani <arshamshirvani@gmail.com>"

register = template.Library()


@register.inclusion_tag(PAGINATOR_TEMPLATE, takes_context=True)
def paginate(context, object_list):
    """
    Creates a paginator element and draws it based on the template
    @type object_list: django.core.paginator.Page
    """

    return paginate_object_list(context['request'].GET.copy(), object_list)
