## Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013 Raik Gruenberg

## This file is part of the rotmic project (https://github.com/graik/rotmic).
## rotmic is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.

## rotmic is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
## You should have received a copy of the GNU Affero General Public
## License along with rotmic. If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime

from django.db import models
from django.db.models.query import QuerySet as Q
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class UserMixin(models.Model):
    """
    Basic record keeping of registration dates and user.
    """

    registeredBy = models.ForeignKey(User, null=False, blank=False, 
                                related_name='%(class)s_created_by',
                                verbose_name='by')
    
    registeredAt = models.DateTimeField(default=datetime.now(), 
                                verbose_name="registered")
    
    class Meta:
        app_label = 'rotmic'        
        abstract = True


class Component(UserMixin):
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
    
    def category(self):
        """
        @return: ComponentType.category
        """
        pass

    class Meta:
        app_label = 'rotmic'
        abstract = False


class DnaComponent(Component):
    """
    Description of a stretch of DNA.
    """
   
    sequence = models.TextField( help_text='nucleotide sequence', blank=True, 
                                 null=True )      
    
    componentType = models.ForeignKey('DnaComponentType', 
                                           verbose_name='Type',
                                           related_name='Type',  blank=False )    
    
    insert = models.ForeignKey( 'self', blank=True, null=True, 
                                        related_name='Insert')
    
    vectorBackbone = models.ForeignKey( 'self', blank=True, null=True ,
                                        verbose_name='Vector Backbone')
    
    marker = models.ManyToManyField( 'self', blank=True, null=True, 
                                      related_name='Marker')
    
##    def related_dnaSamples(self):
##        """
##        """       
##        r = PlasmidSample.objects.filter(dnaComponent=self.id)
##        return r
    
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
          
    def save(self, *args, **kwargs):
        """
        Enforce optional fields depending on category.
        """
        category = self.componentType.category().name

        if category != 'Plasmid':
            self.insert = None
            self.vectorBackbone = None
        
##        ## this part somehow has no effect and leads to bugs.
##        if category not in ['Vector Backbone', 'Insert']:
##            self.marker = Q()
        
        return super(DnaComponent,self).save(*args, **kwargs)
            

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'DNA'

