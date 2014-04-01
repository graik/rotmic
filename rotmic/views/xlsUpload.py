## Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013 - 2014 Raik Gruenberg

## This file is part of the rotmic project (https://github.com/graik/rotmic).
## rotmic is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.

## rotmic is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
## You should have received a copy of the GNU Affero General Public
## License along with rotmic. If not, see <http://www.gnu.org/licenses/>.
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import render

import django.contrib.messages as messages
from django.db import transaction
import django.db.utils as U

import rotmic.models as M
import rotmic.utils.importExcel as I

from rotmic.forms import TableUploadForm


class XlsUploadView(TemplateView):
    """View for uploading Excel files into DnaComponent table"""
    template_name = 'admin/rotmic/uploadXls.html'
   
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
    
    
class ProteinXlsUploadView(XlsUploadView):    
    model = M.ProteinComponent
    parser_class = I.ImportXlsProtein


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

class ProteinSampleXlsUploadView(XlsUploadView):
    model = M.ProteinSample
    parser_class = I.ImportXlsProteinSample
