from django.conf.urls import patterns, include, url

from rotmic.views import view_dnacomponent
from rotmic.jsviews import getTypeDnaInfo, getParentTypeDnaInfo

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rotmicsite.views.home', name='home'),
    # url(r'^rotmicsite/', include('rotmicsite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^rotmic/dna/(?P<displayId>.*)/$',view_dnacomponent,name='dna'),
    url(r'^getTypeDnaInfo/(?P<maintype>.*)/$',getTypeDnaInfo,name='getTypeDnaInfo'),    
    url(r'^getParentTypeDnaInfo/(?P<subtype>.*)/$',getParentTypeDnaInfo,name='getParentTypeDnaInfo'),
##    url(r'^ext/', include('django_select2.urls')),
    url(r'^', include(admin.site.urls)),
)
