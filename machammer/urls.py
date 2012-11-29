from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('main.views',
	url(r'^$', 'index'),
    url(r'^macs/new/$', 'edit_mac'),
    url(r'^scripts/$', 'scripts'),
    url(r'^scripts/(\d+)/$', 'scripts'),
    url(r'^scripts/new/$', 'edit_script'),
	url(r'^updates/$', 'updates'),
    url(r'^workflows/$', 'workflows'),
    url(r'^workflows/new/$', 'edit_workflow', {'wf_id': "new"}),
	url(r'^settings/$', 'settings'),
	url(r'^specs/$', 'specs'),
    url(r'^specs/(\d+)/$', 'specs'),
	url(r'^specs/new/$', 'edit_spec', {'spec_id': "new"}),
    url(r'^specs/(\d+)/edit/$', 'edit_spec'),
	url(r'^updates/(?P<product_id>[\w\-]+)/$', 'updates'),
)
