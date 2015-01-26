from django.utils.text import mark_safe
import jinja2
from jingo import env
from jingo import register
from django_cachedpaginator.utils import PAGINATOR_TEMPLATE, paginate_object_list

__author__ = "Arsham Shirvani <arshamshirvani@gmail.com>"


@register.function
@jinja2.contextfunction
def paginate(context, object_list):
    """
    Creates a paginate function
    @type object_list: django.core.paginator.Page
    """

    template = env.get_template(PAGINATOR_TEMPLATE)
    paginate_dict = paginate_object_list(context['request'].GET.copy(), object_list)
    rendered_template = template.render(paginate_dict)
    return mark_safe(rendered_template)
