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

from django.contrib.contenttypes.models import ContentType

import rotmic.models as M

import rotmic.forms as F

class UpdateManyView(TemplateView):
    """ """
    template_name = 'rotmic/update/updateMany.html'
   
    form_class = F.UpdateManyForm
    
    def renderForm(self, request, form, modelclass=None):
        return render( request, self.template_name, 
                       {'form':form, 'verbose_name':modelclass._meta.verbose_name,
                        'model_name':modelclass._meta.object_name.lower() })
            
    def get(self, request, model='dnacomponent'):
        """Create new form"""
        ## extract sample ids from URL
        initial = {}
        entries = request.GET.get('entries', '')
        if entries:
            initial['entries'] = [ int(x) for x in  entries.split(',') ]
            
        modelclass = ContentType.objects.get(app_label='rotmic',model=model).model_class()

        form = self.form_class(model=modelclass, request=request, initial=initial)
        return self.renderForm(request, form, modelclass=modelclass)
    
    def returnto(self, modelclass=None):
        """Name of view to serve after upload."""
        s = 'admin:%s_%s_changelist' % (modelclass._meta.app_label,
                                        modelclass._meta.object_name.lower())
        return s

    def post(self, request, *args, **kwargs):
        model = kwargs.pop('model', '')
        modelclass = ContentType.objects.get(app_label='rotmic',model=model).model_class()
        
        form = self.form_class(request.POST, request.FILES, request=request,
                               model=modelclass )

        try:
            if not form.is_valid():
                raise ValidationError('form-level validation error')
            
            ## create individual forms
            entry_forms = form.get_forms()
            
            if form._errors:
                raise ValidationError('post-form mapping error')
            
            try:
                with transaction.atomic():
                    
                    for f in entry_forms:
                        f.save()
                        changed = [ f.base_fields[name].label for name in f.changed_data ]
                        changed = 'changed: ' + ', '.join(changed) \
                            if changed else 'nothing changed.'
                        
                        messages.success(request, 
                            u'Updated record %s -- %s' % (unicode(f.instance), changed), 
                            extra_tags='', 
                            fail_silently=False)
                
            except Exception, why:
                messages.error(request, 'Some unforeseen error occured. All updates are reverted. Reason: ' + str(why))

        except ValidationError, why:
            ## re-display with error messages
            return self.renderForm(request, form, modelclass=modelclass)
                
        return HttpResponseRedirect(reverse(self.returnto(modelclass=modelclass)))

