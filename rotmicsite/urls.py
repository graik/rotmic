from django.conf.urls import patterns, include, url

import rotmic.views as V

import rotmicsite.settings as settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^getTypeDnaInfo/(?P<maintype>.*)/$',V.getTypeDnaInfo,name='getTypeDnaInfo'),
    url(r'^getCellTypes/(?P<maintype>.*)/$',V.getCellTypes,name='getCellTypes'),
    url(r'^getChemicalTypes/(?P<maintype>.*)/$',V.getChemicalTypes,name='getChemicalTypes'),
    url(r'^getProteinTypes/(?P<maintype>.*)/$',V.getProteinTypes,name='getProteinTypes'),

    url(r'^rotmic/ajax/nextDnaId/(?P<category>.+)/$', 
        V.nextDnaId, name='nextDnaId' ),

    url(r'^rotmic/ajax/nextCellId/(?P<category>.+)/$', 
        V.nextCellId, name='nextCellId' ),

    url(r'^rotmic/ajax/nextOligoId/$', 
        V.nextOligoId, name='nextOligoId' ),

    url(r'^rotmic/ajax/nextChemicalId/(?P<category>.+)/$', 
        V.nextChemicalId, name='nextChemicalId' ),

    url(r'^rotmic/ajax/nextProteinId/(?P<category>.+)/$', 
        V.nextProteinId, name='nextProteinId' ),

    url(r'^rotmic/ajax/nextSampleId/(?P<container>.+)/$', 
        V.nextSampleId, name='nextSampleId' ),

    url(r'^selectable/', include('selectable.urls')),

    url(r'^rotmic/dnacomponent/(?P<pk>.*)/genbank/$',V.view_genbankfile,name='genbankfile'),
    url(r'^rotmic/proteincomponent/(?P<pk>.*)/genbank/$',V.view_genbankfile_aa,name='genbankfile_aa'),

    url(r'^rotmic/upload/dna/$', V.DnaXlsUploadView.as_view(), name='upload_dnacomponent'),
    url(r'^rotmic/upload/cell/$', V.CellXlsUploadView.as_view(), name='upload_cellcomponent'),
    url(r'^rotmic/upload/oligo/$', V.OligoXlsUploadView.as_view(), name='upload_oligocomponent'),
    url(r'^rotmic/upload/chemical/$', V.ChemicalXlsUploadView.as_view(), name='upload_chemicalcomponent'),
    url(r'^rotmic/upload/protein/$', V.ProteinXlsUploadView.as_view(), name='upload_proteincomponent'),

    url(r'^rotmic/upload/location/$', V.LocationXlsUploadView.as_view(), name='upload_location'),
    url(r'^rotmic/upload/rack/$', V.RackXlsUploadView.as_view(), name='upload_rack'),
    url(r'^rotmic/upload/container/$', V.ContainerXlsUploadView.as_view(), name='upload_container'),

    url(r'^rotmic/upload/dnasample/$', V.DnaSampleXlsUploadView.as_view(), name='upload_dnasample'),
    url(r'^rotmic/upload/oligosample/$', V.OligoSampleXlsUploadView.as_view(), name='upload_oligosample'),
    url(r'^rotmic/upload/chemicalsample/$', V.ChemicalSampleXlsUploadView.as_view(), name='upload_chemicalsample'),
    url(r'^rotmic/upload/cellsample/$', V.CellSampleXlsUploadView.as_view(), name='upload_cellsample'),
    url(r'^rotmic/upload/proteinsample/$', V.ProteinSampleXlsUploadView.as_view(), name='upload_proteinsample'),

    url(r'^rotmic/attach/dna/$', V.GbkUploadView.as_view(), name='attach_dnacomponent'),
    url(r'^rotmic/attach/sequencing/$', V.TracesUploadView.as_view(), name='attach_sequencing'),

    url(r'^', include(admin.site.urls)),
)

if settings.DEBUG:
    ## development user file upload directory
    urlpatterns += patterns('django.views.static',
                            (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}))

