from django.conf.urls.defaults import *
from mingus.urls import urlpatterns as mingus_urlpatterns

urlpatterns = patterns('stereoplex.views',
    url(r'^all/$', 'all', name='stereoplex_all')
) + mingus_urlpatterns

urlpatterns += patterns('',
    (r'^tinymce/', include('tinymce.urls')),
)

