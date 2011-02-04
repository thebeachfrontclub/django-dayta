from django.conf.urls.defaults import *
from jsonrpc import jsonrpc_site
import db.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'db.views.index'),
    url(r'^db/view/(.*)/$', 'db.views.db_view', name='db_view'),
    url(r'^db/design/(.*)/$', 'db.views.db_design', name='db_design'),
    url(r'^db/create/$', 'db.views.db_create', name='db_create'),
    url(r'^json/', jsonrpc_site.dispatch, name='jsonrpc_mountpoint'),
    # Example:
    # (r'^dayta/', include('dayta.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
