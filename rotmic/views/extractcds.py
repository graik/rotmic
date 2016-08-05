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
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView

import rotmic.models as M

class ExtractCDSView(RedirectView):
    
    permanent = False
    query_string = True
    pattern_name = "admin:%s_%s_add" % (M.DnaComponent.Meta.app_label, "dnacomponent")
    
    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        plasmid = get_object_or_404(M.DnaComponent, pk=pk)
        
        kwargs = {'category':'1'}
        
        url = super(ExtractCDSView, self).get_redirect_url(*args, **kwargs)
        return url
