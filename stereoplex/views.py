from django.views.generic import list_detail
from django_proxy.models import Proxy
from view_cache_utils import cache_page_with_prefix
from mingus.core.views import page_key_prefix

@cache_page_with_prefix(60, page_key_prefix)
def all(request, page=0, template_name='proxy/proxy_list.html', **kwargs):
    '''
    Homepage.

    Template: ``proxy/proxy_list.html``
    Context:
        object_list
            Aggregated list of Proxy instances (post, quote, bookmark).

    '''

    posts = Proxy.objects.published().order_by('-pub_date')

    return list_detail.object_list(
        request,
        queryset = posts,
        template_name = template_name,
        **kwargs
    )