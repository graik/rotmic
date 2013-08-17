"""definition of Component Categories (types)"""

from django.db import models


class ComponentType( models.Model ):
    """
    Helper class for classifying parts.
    Following SBOL, each type should in theory correspond to a Sequence Ontology term.
    """
    uri = models.URLField( unique=False, blank=True, null=True,
                           help_text='Typically a sequence ontology URI, example: http://purl.obolibrary.org/obo/SO_0000167' )
    name = models.CharField('Name', unique=True, max_length=200, 
                            help_text='Informative name')

    def __unicode__( self ):
        return unicode(self.name)

    class Meta:
        app_label = 'rotmic' 
        abstract = True


class DnaComponentType( ComponentType ):
    """Classification of DnaComponents"""

    #: required ? directional relationship to parent type or types
    subTypeOf = models.ForeignKey('self', blank=True, 
                            null=True, related_name='subTypes')
    
    def __unicode__(self):
        r = unicode(self.name)
        if self.subTypeOf:
            r = self.subTypeOf.__unicode__() + ' / ' + r
        return r    
  
    class Meta:
        app_label = 'rotmic' 
        verbose_name = 'DNA Type'
        abstract = False
