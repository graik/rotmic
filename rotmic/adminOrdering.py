## Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013-2014 Raik Gruenberg

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
"""Admin interface for Vendor and Ordering-related classes"""

import StringIO
from collections import OrderedDict

from django.contrib import admin, messages
from django.utils import safestring, html

import reversion
from guardian.admin import GuardedModelAdmin
from .utils.customadmin import ViewFirstModelAdmin
from .adminBase import BaseAdminMixin, export_csv

from . import models as M
from . import forms
from .templatetags import rotmicfilters as F
from .utils import adminFilters as filters

## Change to ViewFirstModelAdmin as soon as readonly template is ready
class VendorAdmin(BaseAdminMixin, reversion.VersionAdmin, GuardedModelAdmin):
    """Vendor table Admin interface"""

    fieldsets = ((None, {'fields': (('name',),
                                    ('link', 'login', 'password'),)}),
                 ('Contact', {'fields' : (('contact',),
                                          ('email','phone'),)})
                 )


    list_display = ('name', 'link', 'login', 'password')

    ordering = ('name',)
    search_fields = ('name', 'contact')

    csv_fields = OrderedDict( [('Name', 'name'),
                               ('Link', 'link'),
                               ('Login', 'login'),
                               ('Password', 'password'),
                               ('Contact', 'contact'),
                               ('E-Mail', 'email'),
                               ('Phone', 'phone'),
                               ('Registered','registrationDate()'),
                               ('Author','registeredBy.username'),
                               ('Modified', 'modificationDate()'),
                               ('Modified By','modifiedBy.username'),
                            ])

    actions = ['make_csv']
    

    def make_csv(self, request, queryset):
        return export_csv( request, queryset, self.csv_fields)
    make_csv.short_description = 'Export samples as CSV'

admin.site.register(M.Vendor, VendorAdmin)
