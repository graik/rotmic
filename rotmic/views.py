import StringIO

from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import render

import django.contrib.messages as messages
from django.db import transaction
import django.db.utils as U

import rotmic.models as M
import rotmic.utils.importFiles as I

from rotmic.forms import TableUploadForm


def view_genbankfile(request, pk):
    """DC View"""
    o = M.DnaComponent.objects.get(id=pk)
    txt = o.genbank
    f = StringIO.StringIO( txt )
    
    response = HttpResponse( FileWrapper( f ),
                             content_type='text/gbk')
    
    response['Content-Disposition'] = 'attachment; filename="%s.gbk"' % o.displayId
    
    return response



class XlsUploadView(TemplateView):
    """View for uploading Excel files into DnaComponent table"""
    template_name = 'admin/rotmic/upload.html'
   
    form_class = TableUploadForm
    
    parser_class = I.ImportXlsDna
    
    model = M.DnaComponent
    
    def get(self, request):
        form = self.form_class()
        return render( request, self.template_name, 
                       {'form':form, 'verbose_name':self.model._meta.verbose_name,
                        'model_name':self.model._meta.object_name.lower() })
    
    def returnto(self):
        """
        Name of view to serve after upload.
        """
        s = 'admin:%s_%s_changelist' % (self.model._meta.app_label,
                                        self.model._meta.object_name.lower())
        return s
    
    ## see: https://github.com/axelpale/minimal-django-file-upload-example/blob/master/src/for_django_1-5/myproject/myproject/myapp/views.py
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            
            f = request.FILES['tableFile']
            
            try:
                with transaction.atomic():
                    
                    p = self.parser_class(f, request.user, request=request)
                    p.getObjects(commit=True)
                
                    if p.failed:
                        s = 'Import of %s failed. Correct errors and try again. (Nothing has been imported.)\n' \
                            % (f.name)
                        messages.error(request, s)
                        
                        for d in p.failed:
                            id = d.get('displayId', '??')
                            errors = ['%s (%s)' % (k,v) for k,v in d['errors'].items() ]
                            errors = '; '.join(errors)
        
                            msg = 'Import error(s) for entry "%s": %s' % (id, errors)
                            messages.error(request, msg)
                        
                        raise I.ImportError  ## reverts all transactions
        
                    for o in p.objects:
                        msg = 'Successfully imported %s.' % unicode(o)
                        messages.success(request, msg )
            
            except I.ImportError:
                pass  ## error message is already on top of messages stack
                
            except Exception, why:
                messages.error(request, 'Some unforeseen error occured. All imports are reverted. Reason: ' + str(why))

        else:
            messages.error(request, 'No Excel file given.')
                
        return HttpResponseRedirect(reverse(self.returnto()))


class DnaXlsUploadView(XlsUploadView):    
    model = M.DnaComponent
    parser_class = I.ImportXlsDna
    

class CellXlsUploadView(XlsUploadView):
    model = M.CellComponent
    parser_class = I.ImportXlsCell
    
    
class OligoXlsUploadView(XlsUploadView):
    model = M.OligoComponent
    parser_class = I.ImportXlsOligo
    
    
class ChemicalXlsUploadView(XlsUploadView):
    model = M.ChemicalComponent
    parser_class = I.ImportXlsChemical
    
    
class LocationXlsUploadView(XlsUploadView):
    model = M.Location
    parser_class = I.ImportXlsLocation


class RackXlsUploadView(XlsUploadView):
    model = M.Rack
    parser_class = I.ImportXlsRack    
    
class ContainerXlsUploadView(XlsUploadView):
    model = M.Container
    parser_class = I.ImportXlsContainer

class DnaSampleXlsUploadView(XlsUploadView):
    model = M.DnaSample
    parser_class = I.ImportXlsDnaSample

class OligoSampleXlsUploadView(XlsUploadView):
    model = M.OligoSample
    parser_class = I.ImportXlsOligoSample

class ChemicalSampleXlsUploadView(XlsUploadView):
    model = M.ChemicalSample
    parser_class = I.ImportXlsChemicalSample

class CellSampleXlsUploadView(XlsUploadView):
    model = M.CellSample
    parser_class = I.ImportXlsCellSample
