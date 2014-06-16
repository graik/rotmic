import rotmic.searchforms as S
import rotmic.models as M
import django.shortcuts as D

def search_dnacomponent(request):
    f = S.DnaComponentFilter(request.GET, queryset=M.DnaComponent.objects.all())
    context = {'filter': f,
               'model_name':'dnacomponent',
               'verbose_name':M.DnaComponent._meta.verbose_name}
    return D.render_to_response('rotmic/rotmic_search.html', context)