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
from django.shortcuts import render, render_to_response

import django.contrib.messages as messages
from django.db import transaction

import rotmic.models as M

from rotmic.forms import DnaAnnotationFormSet


class AnnotationEditView(TemplateView):
    """View for editing several annotations for a given DnaComponent"""
    template_name = 'admin/rotmic/annotations.html'
    
    def get(self, request, *args, **kwargs):
        dna = M.DnaComponent.objects.get(pk=kwargs['pk'])
        formset = DnaAnnotationFormSet(instance=dna)
        
        return render( request, self.template_name, 
                       {'formset':formset, 
                        'verbose_name':M.DnaComponent._meta.verbose_name,
                        'component':dna })

    def post(self, request, *args, **kwargs):
        dna = M.DnaComponent.objects.get(pk=kwargs['pk'])
        formset = DnaAnnotationFormSet(request.POST, request.FILES,
                                       instance=dna)
        
        if formset.is_valid():
            formset.save()
        
            return HttpResponseRedirect(dna.get_absolute_url())
        
