"""definition of Component Categories (types)"""

from django.db import models
from django.core.exceptions import ValidationError


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

    def save(self, *args, **kwargs):
        ## enforce single parent?
        return super(ComponentType,self).save(*args, **kwargs)
        
    def clean(self):
        """Enforce single level of type inheritance."""
        assert not type(self) is ComponentType, 'abstract method ComponentType.clean'

        if self.subTypeOf and self.subTypeOf.subTypeOf:
            raise ValidationError('Currently, SubTypeOf only support one level of inheritance')
        
        return super(ComponentType, self).clean()

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
