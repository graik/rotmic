from django.core import serializers
from django.http import HttpResponse
from django.template import loader, Context, RequestContext

from rotmic.models import DnaComponent, DnaComponentType

def view_dnacomponent(request, displayId):
    """DC View"""
    dnaComponent = DnaComponent.objects.get(displayId=displayId)
    t = loader.get_template('view_dnacomponent.html')
    
    html = t.render(Context({'dnaComponent': dnaComponent}))
    return HttpResponse(html)
