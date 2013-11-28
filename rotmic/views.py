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
import django.contrib.messages as messages

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
    import django.utils.safestring as S
    
    if request.method == 'POST':
        form = TableUploadForm(request.POST, request.FILES)
        if form.is_valid():
            
            f = request.FILES['tableFile']
            
            p = ImportXls(f, request.user)
            p.getObjects()
            
            if p.failed:
                msg = 'Import of %s failed. Correct errors and try again. (Nothing has been imported.)\n' \
                    % (f.name)
                messages.error(request, msg)

                for d in p.failed:
                    id = d.get('displayId', '??')
                    errors = ['%s (%s)' % (k,v) for k,v in d['errors'].items() ]
                    errors = '; '.join(errors)

                    msg = 'Import error(s) for entry "%s": %s' % (id, errors)
                    messages.error(request, msg)

            else:
                for f in p.forms:
                    o = f.save()
                    f.save_m2m()

                    msg = 'Successfully imported %s.' % unicode(o)
                    messages.success(request, msg )
            
            return HttpResponseRedirect(reverse('admin:rotmic_dnacomponent_changelist'))
        
    else:
        form = TableUploadForm()
        
    # Render list page with the documents and the form
    return render_to_response(
        'admin/rotmic/upload.html',
        {'form': form},
        context_instance=RequestContext(request)
    )

    