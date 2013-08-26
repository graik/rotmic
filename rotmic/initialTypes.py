"""
Pre-populate database with componentType instances that are needed for templates
and pre-defined actions.
"""
from rotmic.models import DnaComponentType
import logging

def getcreate(typeClass=DnaComponentType, name='', uri=None, subTypeOf=None):
    """
    Look up type of given name or create a new one and save it to the DB.
    """
    try:
        r = typeClass.objects.get(name=name, subTypeOf=subTypeOf)
    except DnaComponentType.DoesNotExist:
        r = DnaComponentType( name=name, uri=uri, subTypeOf=subTypeOf)
        r.save()
        logging.warning('Created missing type: %s %s.' \
                         % (typeClass.__name__, name) )

    return r

## category "root" types
dcPlasmid = getcreate(DnaComponentType, name='Plasmid')
dcVectorBB = getcreate(DnaComponentType, name='Vector Backbone')
dcFragment = getcreate(DnaComponentType, name='Fragment')
dcMarker = getcreate(DnaComponentType, name='Marker')

## Plasmid types
dcPlasmidGeneric = getcreate(DnaComponentType, subTypeOf=dcPlasmid,
                             name='generic plasmid')

## Vector Backbones
dcVectorBacterialHigh = getcreate(DnaComponentType, subTypeOf=dcVectorBB, 
                                  name = 'bacterial expression')
dcVectorBacterialMedium = getcreate(DnaComponentType, subTypeOf=dcVectorBB,
                                    name = 'bacterial cloning')

dcVectorMammalian = getcreate(DnaComponentType, subTypeOf=dcVectorBB, 
                                  name = 'mammalian expression')

dcVectorYeast2M = getcreate(DnaComponentType, subTypeOf=dcVectorBB, 
                                  name = 'yeast 2micron')
dcVectorYeastCentromeric = getcreate(DnaComponentType, subTypeOf=dcVectorBB, 
                                  name = 'yeast centromeric')
dcVectorYeastIntegrating = getcreate(DnaComponentType, subTypeOf=dcVectorBB, 
                                  name = 'yeast integrating')


## Fragments
dcFragmentCDS = getcreate(DnaComponentType, subTypeOf=dcFragment, 
                          name = 'CDS')

dcFragmentProteinPart = getcreate(DnaComponentType, subTypeOf=dcFragment,
                                    name = 'protein part')

dcFragmentIntegration = getcreate(DnaComponentType, subTypeOf=dcFragment,
                                    name = 'integration casette')

dcFragmentConstruction = getcreate(DnaComponentType, subTypeOf=dcFragment,
                                    name = 'construction intermediate')

dcFragmentOther = getcreate(DnaComponentType, subTypeOf=dcFragment,
                                    name = 'other fragment')


## Markers
dcMarkerBacterial = getcreate(DnaComponentType, subTypeOf=dcMarker,
                              name='bacterial resistance')

dcMarkerMammalian = getcreate(DnaComponentType, subTypeOf=dcMarker,
                              name='mammalian resistance')

dcMarkerYeastAuxo = getcreate(DnaComponentType, subTypeOf=dcMarker,
                              name='yeast auxotrophic')
