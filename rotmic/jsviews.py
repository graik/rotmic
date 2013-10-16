from django.core import serializers
import json
from django.http import HttpResponse

from rotmic.models import DnaComponent, DnaComponentType, \
     CellComponent, CellComponentType

import rotmic.utils.ids as I

#### set of methods used to populate categorie and type under Dna and Cell selection,
#### called by Javascript when the user selects a categorie

def getTypeDnaInfo(request, maintype):
    if maintype == -1:
        subtypes = DnaComponentType.objects.all()
    else:    
        subtypes = DnaComponentType.objects.filter(subTypeOf__name=maintype)
    
    json_models = serializers.serialize("json", subtypes)
    return HttpResponse(json_models, mimetype="application/javascript") 

def getCellTypes(request, maintype):
    currentMainType = CellComponentType.objects.filter(subTypeOf__name=maintype)
    
    json_models = serializers.serialize("json", currentMainType)
    return HttpResponse(json_models, mimetype="application/javascript") 

def getParentTypeDnaInfo(request, subtype):
    currentSubType = DnaComponentType.objects.get(id=subtype)
    currentMainType = DnaComponentType.objects.filter(id = currentSubType.subTypeOf.id)
    
    json_models = serializers.serialize("json", currentMainType)
    return HttpResponse(json_models, mimetype="application/javascript") 

def nextDnaId(request, category):
    """
    request - request object
    category - parent ComponentType
    """
    middle = category[0].lower()
    r = {'id': I.suggestDnaId( request.user.id, middle=middle )}
    
    json_models = json.dumps(r)
    return HttpResponse(json_models, mimetype="application/json") 

def nextCellId(request, category):
    """
    request - request object
    category - parent ComponentType
    """
    ## middle = category[0].lower()
    middle = 'c'
    r = {'id': I.suggestCellId( request.user.id, middle=middle )}
    
    json_models = json.dumps(r)
    return HttpResponse(json_models, mimetype="application/json") 

def nextSampleId(request, container):
    """
    request - request object
    container_id - int, pk of selected Container object
    """
    r = {'id': I.suggestSampleId( container ) }
    json_models = json.dumps(r)
    return HttpResponse(json_models, mimetype="application/json") 