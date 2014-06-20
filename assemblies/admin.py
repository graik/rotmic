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

from rotmic.utils import adminFilters as filters
from rotmic.utils.customadmin import ViewFirstModelAdmin
from rotmic.adminBase import UserRecordMixin, RequestFormMixin, export_csv, UpdateManyMixin
from rotmic.adminComponents import ComponentAdminMixin


class AssemblyPartInline(admin.TabularInline):
    model = M.AssemblyPart
    form = forms.AssemblyPartForm
    fk_name = 'assProject'

    can_delete=True
    extra = 2
    max_num = 10
    
    fieldsets = (
        ('Parts', {
            'fields' : (('component', 'bioStart', 'bioEnd', 'strand', 'sequence'),
                        ),
        }),
    )
    
    verbose_name = 'Part'
    verbose_name_plural = '1. Define Parts'

class AssemblyProjectAdmin(RequestFormMixin, ComponentAdminMixin, ViewFirstModelAdmin ):
    
    form = forms.AssemblyProjectForm
    
    inlines = [AssemblyPartInline]
    
    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('authors', 'projects'),
                       ('description',),
                       )
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
    
    list_filter = ['status', 'projects', filters.SortedAuthorFilter]
    
    search_fields = ('displayId', 'name', 'description', 'authors__username',
                     'projects__name')
    

    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name')

admin.site.register(M.AssemblyProject, AssemblyProjectAdmin)