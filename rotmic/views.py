import StringIO

from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.template import loader, Context, RequestContext

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from rotmic.models import DnaComponent, DnaComponentType
from rotmic.utils.importFiles import ImportXls

from rotmic.forms import TableUploadForm
from django.shortcuts import render_to_response

def view_genbankfile(request, pk):
    """DC View"""
    o = DnaComponent.objects.get(id=pk)
    txt = o.genbank
    f = StringIO.StringIO( txt )
    
    response = HttpResponse( FileWrapper( f ),
                             content_type='text/gbk')
    
    response['Content-Disposition'] = 'attachment; filename="%s.gbk"' % o.displayId
    
    return response


## see: https://github.com/axelpale/minimal-django-file-upload-example/blob/master/src/for_django_1-5/myproject/myproject/myapp/views.py
def view_uploadform(request):
    """Upload File Dialog"""
    if request.method == 'POST':
        form = TableUploadForm(request.POST, request.FILES)
        if form.is_valid():
            
            ## parse file and save entries here
            f = request.FILES['tableFile']
            p = ImportXls(f)
            r = p.parse() ## list of dictionaries with key(heading)-value pairs
            
            return HttpResponseRedirect(reverse('admin:rotmic_dnacomponent_changelist'))
        
    else:
        form = TableUploadForm()
    
    # Render list page with the documents and the form
    return render_to_response(
        'admin/rotmic/upload.html',
        {'form': form},
        context_instance=RequestContext(request)
    )