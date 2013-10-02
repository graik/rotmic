"""
Pre-populate database with componentType instances that are needed for templates
and pre-defined actions.
"""
from rotmic.models import DnaComponentType, CellComponentType
import logging

def getcreate(typeClass=DnaComponentType, name='', uri=None, subTypeOf=None,
              **kwargs):
    """
    Look up type of given name or create a new one and save it to the DB.
    """
    try:
        r = typeClass.objects.get(name=name, subTypeOf=subTypeOf)
    except typeClass.DoesNotExist:
        r = typeClass( name=name, uri=uri, subTypeOf=subTypeOf,
                              **kwargs)
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
                          name = 'CDS', isInsert=True)

dcFragmentProteinPart = getcreate(DnaComponentType, subTypeOf=dcFragment,
                                    name = 'protein part', isInsert=True)

dcFragmentIntegration = getcreate(DnaComponentType, subTypeOf=dcFragment,
                                    name = 'integration casette', isInsert=True)

dcFragmentConstruction = getcreate(DnaComponentType, subTypeOf=dcFragment,
                                    name = 'construction intermediate', isInsert=True)

dcFragmentOther = getcreate(DnaComponentType, subTypeOf=dcFragment,
                                    name = 'other fragment')


## Markers
dcMarkerBacterial = getcreate(DnaComponentType, subTypeOf=dcMarker,
                              name='bacterial resistance')

dcMarkerMammalian = getcreate(DnaComponentType, subTypeOf=dcMarker,
                              name='mammalian resistance')

dcMarkerYeastAuxo = getcreate(DnaComponentType, subTypeOf=dcMarker,
                              name='yeast auxotrophic')


## Basic CellComponentTypes

ccEcoli = getcreate(CellComponentType, name='E. coli', 
                    description='Escherichia coli (all strains)')

ccYeast = getcreate(CellComponentType, name='S. cerevisiae',
                    description='S. cerevisiae (all strains)')

ccHuman = getcreate(CellComponentType, name='H. sapiens',
                    description='human cell culture')


## common cell types
ccTop10 = getcreate(CellComponentType, name='Top10',
                    description='standard E. coli cloning strain')

ccMach1 = getcreate(CellComponentType, name='Mach1',
                    description='fast growing E. coli for cloning purposes')

ccBL21 = getcreate(CellComponentType, name='BL21',
                   description='E. coli protein expression strain')

ccHeLa = getcreate(CellComponentType, name='HeLa',
                   description='most classic human cancer cell culture')

ccHek = getcreate(CellComponentType, name='HEK293',
                  description='Human embryonic kidney cells')