from django.conf.urls.defaults import *
from mingus.urls import urlpatterns

urlpatterns += patterns('',
    (r'^tinymce/', include('tinymce.urls')),
)

