from datetime import datetime

from django.db import models
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class UserMixin( models.Model ):
    """
    Basic record keeping of registration dates and user.
    """

    registeredBy = models.ForeignKey(User, null=True, blank=True, 
                                  related_name='%(class)s_created_by')
    
    registeredAt = models.DateTimeField(default=datetime.now(), 
                                    verbose_name="registered")
    
    class Meta:
        app_label = 'rotmic'
        abstract = True


class Component(UserMixin, models.Model):
    """
    Base class for cells, nucleic acids, proteins, and chemicals.
    Not shown to the user (currently) but the table exists and collects
    all fields that are common to all types of Components.
    
    See Meta.abstract
    """

    STATUS_CHOICES = ( ('available', 'available'),
                       ('planning', 'planning'),
                       ('under_construction', 'under construction'),
                       ('abandoned', 'abandoned'))

    displayId = models.CharField('ID', max_length=20, unique=True, 
        help_text='Unique identification')

    name = models.CharField('Name', max_length=200, blank=True, 
                            help_text='Descriptive name (e.g. "TEV protease")')

    comment = models.TextField('Detailed description', blank=True)
    
    status = models.CharField( max_length=30, choices=STATUS_CHOICES, 
                               default='planning')

    def formatedUrl(self):
        name = self.name or ''
        return mark_safe("<a href='/admin/labrack/" +self.get_relative_url() \
                           + "'>" + self.displayId + ' - ' +  name + "</a>")
    
    def __unicode__(self):
        name = self.name or ''
        return u'%s - %s' % (self.displayId, name)


    def showComment( self ):
        """
        @return: str; truncated comment
        """
        if not self.comment:
            return u''
        if len(self.comment) < 40:
            return unicode(self.comment)
        return unicode(self.comment[:38] + '..')
    showComment.short_description = 'Comment'

    class Meta:
        app_label = 'rotmic'
        abstract = False


class DnaComponent(Component):
    """
    Description of a stretch of DNA.
    """
   
    sequence = models.TextField( help_text='nucleotide sequence', blank=True, 
                                 null=True )      
    
##    componentSubType = models.ManyToManyField(DnaComponentType, 
##                                           verbose_name='Type',
##                                           related_name='Type',  blank=True, null=True)    
    
    circular = models.BooleanField( 'Circular', default=True)
    
        
    vectorBackbone = models.ForeignKey( 'self', blank=True, null=True ,
                                        verbose_name='Vector Backbone')
    
    marker = models.ManyToManyField( 'self', blank=True, null=True, 
                                      related_name='Marker')
    
    insert = models.ForeignKey( 'self', blank=True, null=True, 
                                        related_name='Insert')
    
##    def related_dnaSamples(self):
##        """
##        """       
##        r = PlasmidSample.objects.filter(dnaComponent=self.id)
##        return r
    
    def get_user(self):
        name = self.createdBy.username
        return name

##    def get_relative_url(self):
##        """
##        Define standard relative URL for object access in templates
##        """
##        return 'dnacomponent/%i/' % self.id
##    
##    def get_absolute_url(self):
##        """
##        Define standard URL for object views in templates.
##        """
##        return '../../reviewdna/%s/' % self.displayId
   
    def __unicode__(self):
        name = unicode(self.displayId + ' - ' + self.name)
        return name
          
    class Meta:
        app_label = 'rotmic'
        verbose_name = 'DNA'

