from django.core import serializers
from django.http import HttpResponse

from rotmic.models import DnaComponent, DnaComponentType, \
     CellComponent, CellComponentType

#### set of methods used to populate categorie and type under Dna and Cell selection,
#### called by Javascript when the user select a categorie

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

