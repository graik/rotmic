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
from django.forms import ValidationError

import django.contrib.messages as messages
from django.db import transaction
import django.db.utils as U

import rotmic.models as M

from rotmic.forms import TracesUploadForm, GenbankUploadForm

class TracesUploadView(TemplateView):
    """Attach ABL sequencing trace files to existing Sequencing records"""
    template_name = 'admin/rotmic/uploadTraces.html'
   
    form_class = TracesUploadForm
    
    model = M.DnaSample

    def renderForm(self, request, form):
        return render( request, self.template_name, 
                       {'form':form, 'verbose_name':self.model._meta.verbose_name,
                        'model_name':self.model._meta.object_name.lower() })
            
    def get(self, request):
        """Create new form"""
        ## extract sample ids from URL
        initial = {}
        samples = request.GET.get('samples', '')
        if samples:
            initial['samples'] = [ int(x) for x in  samples.split(',') ]

        form = self.form_class(request=request, initial=initial )
        return self.renderForm(request, form)
    
    def returnto(self):
        """Name of view to serve after upload."""
        s = 'admin:%s_%s_changelist' % (self.model._meta.app_label,
                                        self.model._meta.object_name.lower())
        return s

    
    ## see: https://github.com/axelpale/minimal-django-file-upload-example/blob/master/src/for_django_1-5/myproject/myproject/myapp/views.py
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES, request=request)

        try:
            if not form.is_valid():
                raise ValidationError('form-level validation error')
            
            files = request.FILES.getlist('files')

            d = form.mapTracesToSamples(files)
            
            if form._errors:
                raise ValidationError('post-form mapping error')
            
            try:
                with transaction.atomic():
                    
                    for sample, traces in d.items():
                        form.createSeq(sample, traces)
                        messages.success(request, 
                            u'Attached new sequencing record with %i trace files to sample %s' \
                            % (len(traces), unicode(sample)), 
                            extra_tags='', 
                            fail_silently=False)
                
            except Exception, why:
                messages.error(request, 'Some unforeseen error occured. All imports are reverted. Reason: ' + str(why))

        except ValidationError, why:
            ## re-display with error messages
            return self.renderForm(request, form)
                
        return HttpResponseRedirect(reverse(self.returnto()))



class GbkUploadView(TemplateView):
    """Attach genbank files to existing dnacomponent records"""
    template_name = 'admin/rotmic/uploadGbk.html'
   
    form_class = GenbankUploadForm
    
    model = M.DnaComponent
    
    def renderForm(self, request, form):
        return render( request, self.template_name, 
                       {'form':form, 'verbose_name':self.model._meta.verbose_name,
                        'model_name':self.model._meta.object_name.lower() })

    def get(self, request):
        """Create new form"""
        ## extract sample ids from URL
        initial = {}
        constructs = request.GET.get('constructs', '')
        if constructs:
            initial['constructs'] = [ int(x) for x in  constructs.split(',') ]

        form = self.form_class(request=request, initial=initial )
        return self.renderForm(request, form)
    
    def returnto(self):
        """
        Name of view to serve after upload.
        """
        s = 'admin:%s_%s_changelist' % (self.model._meta.app_label,
                                        self.model._meta.object_name.lower())
        return s
    
    ## see: https://github.com/axelpale/minimal-django-file-upload-example/blob/master/src/for_django_1-5/myproject/myproject/myapp/views.py
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES, request=request)

        try:
            if not form.is_valid():
                raise ValidationError('form-level validation error')
            
            d = form.mapGenbankToDna()
            
            if form._errors:
                raise ValidationError('post-form mapping error')
            
            try:
                with transaction.atomic():
                    
                    for dna, gb in d.items():
                        form.attachGenbank(dna, gb)
                        messages.success(request, 
                            u'Attached genbank record to construct %s' \
                            % unicode(dna), 
                            extra_tags='', 
                            fail_silently=False)
                
            except Exception, why:
                messages.error(request, 'Some unforeseen error occured. All imports are reverted. Reason: ' + str(why))

        except ValidationError, why:
            ## re-display with error messages
            return self.renderForm(request, form)
                
        return HttpResponseRedirect(reverse(self.returnto()))
