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
import StringIO

from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

import rotmic.models as M


def view_genbankfile(request, pk):
    """DC genbank file download View"""
    o = M.DnaComponent.objects.get(id=pk)
    txt = o.genbank
    f = StringIO.StringIO( txt )
    
    response = HttpResponse( FileWrapper( f ),
                             content_type='text/gbk')
    
    response['Content-Disposition'] = 'attachment; filename="%s.gbk"' % o.displayId
    
    return response

def view_genbankfile_aa(request, pk):
    """PC genbank file download View"""
    o = M.ProteinComponent.objects.get(id=pk)
    txt = o.genbank
    f = StringIO.StringIO( txt )
    
    response = HttpResponse( FileWrapper( f ),
                             content_type='text/gbk')
    
    response['Content-Disposition'] = 'attachment; filename="%s.gbk"' % o.displayId
    
    return response