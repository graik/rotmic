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
"""Admin interface for DnaAssembly and related classes"""

from django.contrib import admin, messages

from . import models as M
from . import forms
from . import initialTypes as I

from .utils import adminFilters as filters
from .utils.customadmin import ViewFirstModelAdmin
from .adminBase import UserRecordMixin, RequestFormMixin, export_csv, UpdateManyMixin
from .adminComponents import ComponentAdminMixin


class AssemblyLinkInline(admin.TabularInline):
    model = M.AssemblyLink
    form = forms.AssemblyLinkForm
    fk_name = 'assembly'

    can_delete=True
    extra = 4
    max_num = 5
    
    fieldsets = (
        ('Parts', {
            'fields' : (('position','component', 'bioStart', 'bioEnd', 'strand', 'sequence'),
                        ),
        }),
    )
    
    verbose_name = 'Part'
    verbose_name_plural = '1. Define Parts (in exact order)'

class DnaAssemblyAdmin(RequestFormMixin, ComponentAdminMixin, ViewFirstModelAdmin ):
    
    form = forms.DnaAssemblyForm
    
    inlines = [AssemblyLinkInline]
    
    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('method', 'preparedAt', ),
                       )
        }),
        (None, {
            'fields' : (('authors', 'projects'),
                        ('description',),
                        ),
        }),            
    )

    list_display = ('displayId',
                    'name',
                    'showStatus',
                    'showComments',
                    'registrationDate',
                    'showFirstAuthor',
                    'showDescription', 
                    'showEdit' 
                   )
    
    list_filter = ['status', 'method', 'projects', filters.SortedAuthorFilter]
    
    search_fields = ('displayId', 'name', 'description', 'authors__username',
                     'projects__name')
    

    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name')

admin.site.register(M.DnaAssembly, DnaAssemblyAdmin)