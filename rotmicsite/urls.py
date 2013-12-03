from django.conf.urls import patterns, include, url

from rotmic.views import view_genbankfile, DnaXlsUploadView, CellXlsUploadView,\
     OligoXlsUploadView, ChemicalXlsUploadView
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

    url(r'^rotmic/dnacomponent/(?P<pk>.*)/genbank/$',view_genbankfile,name='genbankfile'),

    url(r'^rotmic/upload/dna/$', DnaXlsUploadView.as_view(), name='upload_dnacomponent'),
    url(r'^rotmic/upload/cell/$', CellXlsUploadView.as_view(), name='upload_cellcomponent'),
    url(r'^rotmic/upload/oligo/$', OligoXlsUploadView.as_view(), name='upload_oligocomponent'),
    url(r'^rotmic/upload/chemical/$', ChemicalXlsUploadView.as_view(), name='upload_chemicalcomponent'),

    url(r'^', include(admin.site.urls)),
)

if settings.DEBUG:
    ## development user file upload directory
    urlpatterns += patterns('django.views.static',
                            (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}))

