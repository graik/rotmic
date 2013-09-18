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
import re

from django.db import models
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class UserMixin(models.Model):
    """
    Basic record keeping of registration dates and user.
    """

    registeredBy = models.ForeignKey(User, null=False, blank=False, 
                                related_name='%(class)s_created_by',
                                verbose_name='author')
    
    registeredAt = models.DateTimeField(default=datetime.now(), 
                                verbose_name="registered")
    
    modifiedBy = models.ForeignKey(User, null=True, blank=False, 
                                related_name='%(class)s_modified_by',
                                verbose_name='modified by')
    
    modifiedAt = models.DateTimeField(default=datetime.now(), 
                                verbose_name="modified")
    
    
    def registrationDate(self):
        """extract date from date+time"""
        return self.registeredAt.date().isoformat()
    registrationDate.short_description = 'registered'
    
    def registrationTime(self):
        """extract time from date+time"""
        return self.registeredAt.time()
    registrationTime.short_description = 'at'

    def modificationDate(self):
        """extract date from date+time"""
        return self.modifiedAt.date().isoformat()
    modificationDate.short_description = 'modified'

    def modificationTime(self):
        """extract time from date+time"""
        return self.modifiedAt.time()
    modificationTime.short_description = 'at'

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
    upload_to = 'attachments/Component'

    STATUS_CHOICES = ( ('available', 'available'),
                       ('planning', 'planning'),
                       ('construction', 'construction'),
                       ('abandoned', 'abandoned'))

    displayId = models.CharField('ID', max_length=20, unique=True, 
        help_text='Unique identification')

    name = models.CharField('Name', max_length=200, blank=True, 
                            help_text='Descriptive name (e.g. "eGFP_pUC19")')

    comment = models.TextField('Description', blank=True,
                help_text='You can format your text and include links. See: <a href="http://daringfireball.net/projects/markdown/basics">Markdown Quick Reference</a>')
    
    status = models.CharField( max_length=30, choices=STATUS_CHOICES, 
                               default='planning')
    
    def __unicode__(self):
        name = self.name or ''
        return u'%s - %s' % (self.displayId, name)

    def commentText(self):
        """remove some formatting characters from text"""
        r = re.sub('--','', self.comment)
        r = re.sub('=','', r)
        r = re.sub('__','', r)
        return r
    commentText.short_description = 'description'


    class Meta:
        app_label = 'rotmic'
        abstract = False



class DnaComponent(Component):
    """
    Description of a stretch of DNA.
    """
   
    sequence = models.TextField( help_text='nucleotide sequence', blank=True, 
                                 null=True )
    
    genbank = models.TextField( help_text='genbank file content', blank=True,
                                null=True )
    
    componentType = models.ForeignKey('DnaComponentType', 
                                      verbose_name='Type',
                                      blank=False )    
    
    insert = models.ForeignKey( 'self', blank=True, null=True,
                                related_name='as_insert_in_dna+',
                                help_text='start typing for auto-completion')
    
    vectorBackbone = models.ForeignKey( 'self', blank=True, null=True ,
                                        verbose_name='Vector Backbone',
                                        related_name='as_vector_in_plasmid',
                                        help_text='start typing for auto-completion')
    
    marker = models.ManyToManyField( 'self', blank=True, null=True, 
                                     symmetrical=False,
                                     related_name='as_marker_in_dna',   ## end with + to suppress reverse relationship
                                     verbose_name='Selection markers')
    
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
    def get_absolute_url(self):
        """
        Define standard URL for object views
        see: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#reversing-admin-urls
        """
        from django.core.urlresolvers import reverse
        return reverse('admin:rotmic_dnacomponent_readonly', args=(self.id,))
    
    def get_absolute_url_edit(self):
        from django.core.urlresolvers import reverse
        return reverse('admin:rotmic_dnacomponent_change', args=(self.id,))
   

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


    def allMarkers( self ):
        """
        @return: [DnaComponent]
        All markers contained in this DC directly or within a linked
        insert or vector backbone.
        """
        r = []
        if self.marker:
            r += self.marker.all()
        if self.vectorBackbone:
            r += [ m for m in self.vectorBackbone.allMarkers() if not m in r ]
        if self.insert:
            r += [ m for m in self.insert.allMarkers() if not m in r ]
        return r
            

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'DNA construct'
        ordering = ['displayId']


class CellComponent(Component):
    """
    Description of a cell (modified or not)
    """
    componentType = models.ForeignKey('CellComponentType', 
                                      verbose_name='Species',
                                      blank=False )    
    
    plasmid = models.ForeignKey( 'DnaComponent', blank=True, null=True, 
                                 verbose_name='Plasmid',
                                 related_name='as_plasmid_in_cell',
                                 help_text='start typing for auto-completion')
    
    marker = models.ManyToManyField( 'DnaComponent', blank=True, null=True, 
                                      related_name='as_marker_in_cell',
                                      verbose_name='genomic markers',
                                      help_text='start typing...')
    
        
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
    def get_absolute_url(self):
        """
        Define standard URL for object views
        see: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#reversing-admin-urls
        """
        from django.core.urlresolvers import reverse
        return reverse('admin:rotmic_cellcomponent_readonly', args=(self.id,))
    
    def get_absolute_url_edit(self):
        from django.core.urlresolvers import reverse
        return reverse('admin:rotmic_cellcomponent_change', args=(self.id,))
   

    def __unicode__(self):
        name = unicode(self.displayId + ' - ' + self.name)
        return name
          
    def save(self, *args, **kwargs):
        """
        Enforce optional fields depending on category.
        """
        category = self.componentType.category().name

        if not self.componentType.allowPlasmids:
            self.plasmid = None
            
        return super(CellComponent,self).save(*args, **kwargs)
            

    def allMarkers( self ):
        """
        @return: [DnaComponent]
        All markers contained in this cell directly or within a linked
        plasmid.
        """
        r = []
        if self.marker:
            r += [ m for m in self.marker.all() if not m in r ]
        if self.plasmid:
            r += [ m for m in self.plasmid.allMarkers() if not m in r ]
        return r

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'Cell'
        ordering = ['displayId']

