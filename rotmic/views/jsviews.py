from django.core import serializers
import json
from django.http import HttpResponse

import rotmic.models as M

import rotmic.utils.ids as I

#### set of methods used to populate categorie and type under Dna and Cell selection,
#### called by Javascript when the user selects a categorie

def categoryTypes(request, typeclass, **kwargs):
    """@return json, all child ComponentTypes of given Category"""
    T = M.__dict__[typeclass]
    cat = request.GET['category_id']
    subtypes = T.objects.filter(subTypeOf__id=int(cat))
    
    json_models = serializers.serialize("json", subtypes)
    return HttpResponse(json_models, mimetype="application/javascript") 


def nextId(request, modelclass):
    """
    request - request object
    category - parent ComponentType
    """
    mclass = M.__dict__[modelclass]
    cat = int(request.GET.get('category_id', -1))
    
    r = {'id': I.nextId( mclass, request.user, category_id=cat )}
    
    json_models = json.dumps(r)
    return HttpResponse(json_models, mimetype="application/json") 



##def getParentTypeDnaInfo(request, subtype):
##    currentSubType = M.DnaComponentType.objects.get(id=subtype)
##    currentMainType = M.DnaComponentType.objects.filter(id = currentSubType.subTypeOf.id)
##    
##    json_models = serializers.serialize("json", currentMainType)
##    return HttpResponse(json_models, mimetype="application/javascript") 


def nextSampleId(request, container):
    """
    request - request object
    container_id - int, pk of selected Container object
    """
    r = {'id': I.suggestSampleId( container ) }
    json_models = json.dumps(r)
    return HttpResponse(json_models, mimetype="application/json") 