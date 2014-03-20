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
"""Extension of default User admin"""

from django.contrib import admin

import reversion

from .utils.customadmin import ViewFirstModelAdmin
from .adminBase import BaseAdminMixin, export_csv

import models as M

class ProjectAdmin(BaseAdminMixin, reversion.VersionAdmin, ViewFirstModelAdmin):
    ## form = forms.LocationForm
    
    ## change_form_template = 'admin/rotmic/change_form_viewfirst.html'  ## adapt breadcrums to view first admin

    ## change_list_template = "admin/rotmic/location/change_list.html"

    fieldsets = [
        (None, {
            'fields' : ((('name'),
                         ('description',)
                        )),
            'description' : 'Describe a projects to bundle constructs into.',
            }
         )
        ]

    list_display = ('name', 'showDescription')
    search_fields = ('name', 'description')

    save_as = True

admin.site.register( M.Project, ProjectAdmin )
