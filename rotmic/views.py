import StringIO

from django.core import serializers
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.template import loader, Context, RequestContext

from rotmic.models import DnaComponent, DnaComponentType


def view_genbankfile(request, pk):
    """DC View"""
    o = DnaComponent.objects.get(id=pk)
    txt = o.genbank
    f = StringIO.StringIO( txt )
    
    response = HttpResponse( FileWrapper( f ),
                             content_type='text/gbk')
    
    response['Content-Disposition'] = 'attachment; filename="%s.gbk"' % o.displayId
    
    return response
