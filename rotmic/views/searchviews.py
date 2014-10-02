import rotmic.searchforms as S
import rotmic.models as M

import django.shortcuts as D
from django.contrib.contenttypes.models import ContentType

def search_dnacomponent(request, model='dnacomponent'):
    try:
        modelclass = ContentType.objects.get(app_label='rotmic',model=model).model_class()
        filterclass = S.__dict__[modelclass.__name__ + 'Filter']
    except:
        raise LookupError, 'no filter available for ' + model
    
    f = filterclass(request.GET, queryset=modelclass.objects.all())
    context = {'filter': f,
               'model_name':model,
               'verbose_name':modelclass._meta.verbose_name}
    return D.render_to_response('rotmic/rotmic_search.html', context)