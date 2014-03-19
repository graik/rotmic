"""
Pre-populate database with componentType instances that are needed for templates
and pre-defined actions.
"""
import rotmic.models as M

import logging

def getcreate(typeClass=M.DnaComponentType, name='', **kwargs):
    """
    Look up type of given name or create a new one and save it to the DB.
    """
    try:
        r = typeClass.objects.get(name=name)
    except typeClass.DoesNotExist:
        r = typeClass( name=name, **kwargs)
        r.save()
        logging.warning('Created missing type: %s %s.' % (typeClass.__name__, name) )

    return r

## category "root" types (all required)
dcPlasmid = getcreate(M.DnaComponentType, name='Plasmid')
dcVectorBB = getcreate(M.DnaComponentType, name='Vector Backbone')
dcFragment = getcreate(M.DnaComponentType, name='Fragment')
dcMarker = getcreate(M.DnaComponentType, name='Marker')

## Plasmid types (optional)
dcPlasmidGeneric = getcreate(M.DnaComponentType, subTypeOf=dcPlasmid,
                             name='generic plasmid')

## Vector Backbones

## required:
dcVectorUndefined = getcreate(M.DnaComponentType, subTypeOf=dcVectorBB,
                              name='undefined vector')


## all optional:
dcVectorBacterialHigh = getcreate(M.DnaComponentType, subTypeOf=dcVectorBB, 
                                  name = 'bacterial expression')
dcVectorBacterialMedium = getcreate(M.DnaComponentType, subTypeOf=dcVectorBB,
                                    name = 'bacterial cloning')

dcVectorMammalian = getcreate(M.DnaComponentType, subTypeOf=dcVectorBB, 
                                  name = 'mammalian expression')

dcVectorYeast2M = getcreate(M.DnaComponentType, subTypeOf=dcVectorBB, 
                                  name = 'yeast 2micron')
dcVectorYeastCentromeric = getcreate(M.DnaComponentType, subTypeOf=dcVectorBB, 
                                  name = 'yeast centromeric')
dcVectorYeastIntegrating = getcreate(M.DnaComponentType, subTypeOf=dcVectorBB, 
                                  name = 'yeast integrating')



## Fragments (all optional)
dcFragmentCDS = getcreate(M.DnaComponentType, subTypeOf=dcFragment, 
                          name = 'CDS', isInsert=True)

dcFragmentProteinPart = getcreate(M.DnaComponentType, subTypeOf=dcFragment,
                                    name = 'protein part', isInsert=True)

dcFragmentIntegration = getcreate(M.DnaComponentType, subTypeOf=dcFragment,
                                    name = 'integration casette', isInsert=True)

dcFragmentConstruction = getcreate(M.DnaComponentType, subTypeOf=dcFragment,
                                    name = 'construction intermediate', isInsert=True)

dcFragmentOther = getcreate(M.DnaComponentType, subTypeOf=dcFragment,
                                    name = 'other fragment')


## Markers (all optional)
dcMarkerBacterial = getcreate(M.DnaComponentType, subTypeOf=dcMarker,
                              name='bacterial resistance')

dcMarkerMammalian = getcreate(M.DnaComponentType, subTypeOf=dcMarker,
                              name='mammalian resistance')

dcMarkerYeastAuxo = getcreate(M.DnaComponentType, subTypeOf=dcMarker,
                              name='yeast auxotrophic')

###########################
## Basic CellComponentTypes

## required:
ccEcoli = getcreate(M.CellComponentType, name='E. coli', 
                    description='Escherichia coli (all strains)')

## optional:
ccYeast = getcreate(M.CellComponentType, name='S. cerevisiae',
                    description='S. cerevisiae (all strains)')

ccHuman = getcreate(M.CellComponentType, name='H. sapiens',
                    description='human cell culture')

## common cell types (all optional)
ccTop10 = getcreate(M.CellComponentType, name='Top10', subTypeOf=ccEcoli,
                    allowMarkers=True,
                    description='standard E. coli cloning strain')

ccMach1 = getcreate(M.CellComponentType, name='Mach1', subTypeOf=ccEcoli,
                    allowMarkers=True,
                    description='fast growing E. coli for cloning purposes')

ccBL21 = getcreate(M.CellComponentType, name='BL21', subTypeOf=ccEcoli,
                   allowMarkers=False,
                   description='E. coli protein expression strain')

ccHeLa = getcreate(M.CellComponentType, name='HeLa', subTypeOf=ccHuman,
                   allowMarkers=False,
                   description='most classic human cancer cell culture')

ccHek = getcreate(M.CellComponentType, name='HEK293', subTypeOf=ccHuman,
                  allowMarkers=False,
                  description='Human embryonic kidney cells')


##############################
## Oligo types (all required):

ocStandard = getcreate(M.OligoComponentType, name='standard',
                       description='standard oligonucleotide for PCR reactions')

ocSequencing = getcreate(M.OligoComponentType, name='sequencing',
                       description='Primer for sequencing reactions')


#################
## Chemical types

## required:
chemReagent = getcreate(M.ChemicalType, name='Reagent', subTypeOf=None)

chemOther = getcreate(M.ChemicalType, name='other reagent', subTypeOf=chemReagent)

#### optional:
##chemBio = getcreate(M.ChemicalType, name='biological', subTypeOf=None)
##
##chemAB = getcreate(M.ChemicalType, name='antibody', subTypeOf=chemBio)
##
##chemEnzyme = getcreate(M.ChemicalType, name='enzyme', subTypeOf=chemBio)

#################
## Protein types

## required:
pcProtein = getcreate(M.ProteinComponentType, name='Protein', subTypeOf=None)

pcOther = getcreate(M.ProteinComponentType, name='other protein', subTypeOf=pcProtein)
