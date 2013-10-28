from django.core import serializers
import json
from django.http import HttpResponse

import rotmic.models as M

import rotmic.utils.ids as I

#### set of methods used to populate categorie and type under Dna and Cell selection,
#### called by Javascript when the user selects a categorie

def getTypeDnaInfo(request, maintype):
    if maintype == -1:
        subtypes = M.DnaComponentType.objects.all()
    else:    
        subtypes = M.DnaComponentType.objects.filter(subTypeOf__name=maintype)
    
    json_models = serializers.serialize("json", subtypes)
    return HttpResponse(json_models, mimetype="application/javascript") 

def getCellTypes(request, maintype):
    if maintype.isdigit():  ## support identification by primary key
        subtypes = M.CellComponentType.objects.filter(subTypeOf__id=int(maintype))
    else:
        subtypes = M.CellComponentType.objects.filter(subTypeOf__name=maintype)
    
    json_models = serializers.serialize("json", subtypes)
    return HttpResponse(json_models, mimetype="application/javascript") 

def getChemicalTypes(request, maintype):
    if maintype.isdigit():  ## support identification by primary key
        subtypes = M.ChemicalComponentType.objects.filter(subTypeOf__id=int(maintype))
    else:
        subtypes = M.ChemicalType.objects.filter(subTypeOf__name=maintype)
    
    json_models = serializers.serialize("json", subtypes)
    return HttpResponse(json_models, mimetype="application/javascript") 


def getParentTypeDnaInfo(request, subtype):
    currentSubType = M.DnaComponentType.objects.get(id=subtype)
    currentMainType = M.DnaComponentType.objects.filter(id = currentSubType.subTypeOf.id)
    
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

def nextOligoId(request):
    """
    request - request object
    """
    ## middle = category[0].lower()
    middle = 'o'
    r = {'id': I.suggestOligoId( request.user.id, middle=middle )}
    
    json_models = json.dumps(r)
    return HttpResponse(json_models, mimetype="application/json") 


def nextChemicalId(request, category):
    """
    request - request object
    category - ignored for now
    """
    r = {'id': I.suggestChemicalId( request.user.id )}
    
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