from django.conf.urls import patterns, include, url

from rotmic.views import view_genbankfile
from rotmic.jsviews import getTypeDnaInfo, getCellTypes, nextDnaId, nextCellId
import rotmicsite.settings as settings

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
    url(r'^getCellTypes/(?P<maintype>.*)/$',getCellTypes,name='getCellTypes'),

    url(r'^rotmic/ajax/nextDnaId/(?P<category>.+)/$', 
        nextDnaId, name='nextDnaId' ),

    url(r'^rotmic/ajax/nextCellId/(?P<category>.+)/$', 
        nextCellId, name='nextCellId' ),

    url(r'^selectable/', include('selectable.urls')),
    url(r'^rotmic/dnacomponent/(?P<pk>.*)/genbank/$',view_genbankfile,name='genbankfile'),
    url(r'^', include(admin.site.urls)),
)

if settings.DEBUG:
    ## development user file upload directory
    urlpatterns += patterns('django.views.static',
                            (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}))

