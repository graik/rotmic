"""definition of Component Categories (types)"""

from django.db import models
from django.core.exceptions import ValidationError


class ComponentType( models.Model ):
    """
    Helper class for classifying parts.
    Following SBOL, each type should in theory correspond to a Sequence Ontology term.
    """
    name = models.CharField('Name', unique=True, max_length=200, 
                            help_text='Informative name')
    
    description = models.CharField('Description', blank=True, max_length=200,
                                   help_text='short description for users')

    uri = models.URLField( unique=False, blank=True, null=True,
                           help_text='Typically a sequence ontology URI, example: http://purl.obolibrary.org/obo/SO_0000167' )

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
    
    def category(self):
        """Return parent type if any or self"""
        if self.subTypeOf:
            return self.subTypeOf.category()
        return self

    class Meta:
        app_label = 'rotmic' 
        abstract = True


class DnaComponentType( ComponentType ):
    """Classification of DnaComponents"""

    #: directional relationship to parent type or types
    subTypeOf = models.ForeignKey('self', blank=True, null=True,
                                  limit_choices_to={'subTypeOf':None},
                                  related_name='subTypes',
                                  help_text='Assign to existing category or leave blank to create a new top-level category')
    
    isInsert = models.BooleanField('allow as insert', default=False,
                                   help_text='Are fragments of this type selectable as inserts in plasmids?')
    
    def __unicode__(self):
        r = unicode(self.name)
        if self.subTypeOf:
            r = self.subTypeOf.__unicode__() + ' / ' + r
        return r    
  
    class Meta:
        app_label = 'rotmic' 
        verbose_name = 'DNA Type'
        abstract = False
