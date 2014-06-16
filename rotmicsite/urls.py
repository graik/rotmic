from django.conf.urls import patterns, include, url

import rotmic.views as V

import rotmicsite.settings as settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ## custom javascript URLS

    url(r'^rotmic/ajax/categoryTypes/(?P<typeclass>.+)/$', 
        V.categoryTypes, name='categoryTypes' ),

    url(r'^rotmic/ajax/nextId/(?P<modelclass>.+)/$', 
        V.nextId, name='nextId' ),


    url(r'^rotmic/ajax/nextSampleId/(?P<container>.+)/$', 
        V.nextSampleId, name='nextSampleId' ),
    
    ## autocomplete fields javascript
    url(r'^selectable/', include('selectable.urls')),

    ## genbankfile download
    url(r'^rotmic/dnacomponent/(?P<pk>.*)/genbank/$',V.view_genbankfile,name='genbankfile'),
    url(r'^rotmic/proteincomponent/(?P<pk>.*)/genbank/$',V.view_genbankfile_aa,name='genbankfile_aa'),

    ## Excel upload
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

    ## genbank and trace file bulk upload
    url(r'^rotmic/upload/genbank/$', V.GbkUploadView.as_view(), name='upload_genbank'),
    url(r'^rotmic/upload/genbankaa/$', V.GbkProteinUploadView.as_view(), name='upload_proteingenbank'),
    url(r'^rotmic/upload/tracefiles/$', V.TracesUploadView.as_view(), name='upload_tracefiles'),

    ## other
    (r'^comments/', include('ratedcomments.urls')),

    ## bulk update dialog
    url(r'^rotmic/update/(?P<model>.+)/$', V.UpdateManyView.as_view(), name='update_many'),  
    
    ## search dialog
    url(r'^rotmic/search/(?P<model>.+)/$', V.search_dnacomponent, name='search'),

    url(r'^', include(admin.site.urls)),
)

if settings.DEBUG:
    ## development user file upload directory
    urlpatterns += patterns('django.views.static',
                            (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}))

