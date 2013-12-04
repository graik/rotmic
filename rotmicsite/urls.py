from django.conf.urls import patterns, include, url

import rotmic.views as V

from rotmic.jsviews import getTypeDnaInfo, getCellTypes, nextDnaId, \
     nextCellId, nextSampleId, nextOligoId, getChemicalTypes, nextChemicalId
import rotmicsite.settings as settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^getTypeDnaInfo/(?P<maintype>.*)/$',getTypeDnaInfo,name='getTypeDnaInfo'),
    url(r'^getCellTypes/(?P<maintype>.*)/$',getCellTypes,name='getCellTypes'),
    url(r'^getChemicalTypes/(?P<maintype>.*)/$',getChemicalTypes,name='getChemicalTypes'),

    url(r'^rotmic/ajax/nextDnaId/(?P<category>.+)/$', 
        nextDnaId, name='nextDnaId' ),

    url(r'^rotmic/ajax/nextCellId/(?P<category>.+)/$', 
        nextCellId, name='nextCellId' ),

    url(r'^rotmic/ajax/nextOligoId/$', 
        nextOligoId, name='nextOligoId' ),

    url(r'^rotmic/ajax/nextChemicalId/(?P<category>.+)/$', 
        nextChemicalId, name='nextChemicalId' ),

    url(r'^rotmic/ajax/nextSampleId/(?P<container>.+)/$', 
        nextSampleId, name='nextSampleId' ),

    url(r'^selectable/', include('selectable.urls')),

    url(r'^rotmic/dnacomponent/(?P<pk>.*)/genbank/$',V.view_genbankfile,name='genbankfile'),

    url(r'^rotmic/upload/dna/$', V.DnaXlsUploadView.as_view(), name='upload_dnacomponent'),
    url(r'^rotmic/upload/cell/$', V.CellXlsUploadView.as_view(), name='upload_cellcomponent'),
    url(r'^rotmic/upload/oligo/$', V.OligoXlsUploadView.as_view(), name='upload_oligocomponent'),
    url(r'^rotmic/upload/chemical/$', V.ChemicalXlsUploadView.as_view(), name='upload_chemicalcomponent'),

    url(r'^rotmic/upload/location/$', V.LocationXlsUploadView.as_view(), name='upload_location'),
    url(r'^rotmic/upload/rack/$', V.RackXlsUploadView.as_view(), name='upload_rack'),
    url(r'^rotmic/upload/container/$', V.ContainerXlsUploadView.as_view(), name='upload_container'),

    url(r'^rotmic/upload/dnasample/$', V.DnaSampleXlsUploadView.as_view(), name='upload_dnasample'),
    url(r'^rotmic/upload/oligosample/$', V.OligoSampleXlsUploadView.as_view(), name='upload_oligosample'),
    url(r'^rotmic/upload/chemicalsample/$', V.ChemicalSampleXlsUploadView.as_view(), name='upload_chemicalsample'),

    url(r'^', include(admin.site.urls)),
)

if settings.DEBUG:
    ## development user file upload directory
    urlpatterns += patterns('django.views.static',
                            (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}))

