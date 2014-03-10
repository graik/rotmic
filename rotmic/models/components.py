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
import django.utils.html as html
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User, Group

import rotmic.templatetags.rotmicfilters as F
import rotmic.utils.inheritance as I


class UserMixin(models.Model):
    """
    Basic record keeping of registration dates and user.
    """

    registeredBy = models.ForeignKey(User, null=False, blank=False, 
                                related_name='%(class)s_created_by',
                                verbose_name='Author')
    
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

    displayId = models.CharField('ID', max_length=20, unique=True, 
        help_text='Unique identification')

    name = models.CharField('Name', max_length=200, blank=True, 
                            help_text='short descriptive name')

    description = models.TextField('Description', blank=True,
                help_text='You can format your text and include links. See: <a href="http://daringfireball.net/projects/markdown/basics">Markdown Quick Reference</a>')
    
    ## return child classes in queries using select_subclasses()
    objects = I.InheritanceManager()  

    def __unicode__(self):
        name = self.name or ''
        return u'%s (%s)' % (self.displayId, name)

    def get_absolute_url(self):
        """
        Define standard URL for object views
        see: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#reversing-admin-urls
        """
        classname = self.__class__.__name__.lower()
        return reverse('admin:rotmic_%s_readonly' % classname, args=(self.id,))
    
    def get_absolute_url_edit(self):
        classname = self.__class__.__name__.lower()
        return reverse('admin:rotmic_%s_change' % classname, args=(self.id,))
   
    def descriptionText(self):
        """remove some formatting characters from text"""
        r = re.sub('--','', self.description)
        r = re.sub('=','', r)
        r = re.sub('__','', r)
        return r
    descriptionText.short_description = 'description'

    def showDescription(self):
        """
        @return: str; truncated description with full description mouse-over
        """
        if not self.description: 
            return u''
        if len(self.description) < 40:
            return unicode(self.description)
        r = unicode(self.description[:38])
        r = html.mark_safe('<a title="%s">%s</a>' \
                           % (self.description, F.truncate(self.descriptionText(), 40)))
        return r
    showDescription.allow_tags = True
    showDescription.short_description = 'Description'

    class Meta:
        app_label = 'rotmic'
        abstract = False



class StatusMixin:
    def statusValue(self):
        """@return str, human-readable version of status flag"""
        for flag, value in self.STATUS_CHOICES:
            if flag == self.status:
                return value
        return 'unknown'
    
class StatusMixinDna(models.Model, StatusMixin):
    
    STATUS_CHOICES = ( ('available', 'available'),
                       ('planning', 'planning'),
                       ('construction', 'construction'),
                       ('abandoned', 'abandoned'))

    status = models.CharField( max_length=30, choices=STATUS_CHOICES, 
                               default='planning')
    
    class Meta:
        abstract = True
    

class DnaComponent(Component, StatusMixinDna):
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
                                related_name='as_insert_in_dna',
                                help_text='start typing for auto-completion')
    
    vectorBackbone = models.ForeignKey( 'self', blank=True, null=True ,
                                        verbose_name='Vector Backbone',
                                        related_name='as_vector_in_plasmid',
                                        help_text='start typing for auto-completion')
    
    markers = models.ManyToManyField( 'self', blank=True, null=True, 
                                     symmetrical=False,
                                     related_name='as_marker_in_dna',   ## end with + to suppress reverse relationship
                                     verbose_name='Selection markers',
                                     help_text='start typing ID or name')
    
    translatesTo = models.ForeignKey('ProteinComponent',
                                     verbose_name='Translates to protein',
                                     related_name='codingSequences',
                                     null=True, blank=True)
    
    
    def relatedDnaDict(self):
        """
        DNA components that (directly) contain this dna component.
        @return (str, DnaComponent) -- (relationship, related component)
        """
        r = {}
        if self.as_insert_in_dna.count():
            r['insert'] = self.as_insert_in_dna.all()
        if self.as_vector_in_plasmid.count():
            r['vectorbackbone'] = self.as_vector_in_plasmid.all()
        if self.as_marker_in_dna.count():
            r['markers'] = self.as_marker_in_dna.all()
        return r
    
    def relatedDnaCount(self):
        """@return int -- number of related DnaComponent objects"""
        return sum( map(len, self.relatedDnaDict().values()) )
    
    def allSamples(self):
        """
        DNA and cell samples for this construct.
        """
        from . import CellSample
        dnasamples = self.dna_samples.all()

        sample_ids = self.as_plasmid_in_cell.values_list('cell_samples', flat=True)
        sample_ids = [ i for i in sample_ids if i ] ## filter out None
        cellsamples = CellSample.objects.filter(id__in=sample_ids)

        return list(dnasamples) + list(cellsamples)
    
    def allSamplesCount(self):
        dna = self.dna_samples.count()
        
        sample_ids= self.as_plasmid_in_cell.values_list('cell_samples', flat=True)
        sample_ids = [ i for i in sample_ids if i ] ## filter out None
        
        return dna + len(sample_ids)

    def save(self, *args, **kwargs):
        """
        Enforce optional fields depending on category.
        """
        category = self.componentType.category().name

        if category != 'Plasmid':
            self.insert = None
            self.vectorBackbone = None
        
        return super(DnaComponent,self).save(*args, **kwargs)


    def allMarkers( self ):
        """
        @return: [DnaComponent]
        All markers contained in this DC directly or within a linked
        insert or vector backbone.
        """
        r = []
        if self.markers.count():
            r += self.markers.all()
        if self.vectorBackbone:
            r += [ m for m in self.vectorBackbone.allMarkers() if not m in r ]
        if self.insert:
            r += [ m for m in self.insert.allMarkers() if not m in r ]
        return r
            

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'DNA construct'
        ordering = ['displayId']


class CellComponent(Component, StatusMixinDna):
    """
    Description of a cell (modified or not)
    """
    componentType = models.ForeignKey('CellComponentType', 
                                      verbose_name='Strain',
                                      blank=False )    
    
    # convert to many2many ?
    plasmid = models.ForeignKey( 'DnaComponent', blank=True, null=True, 
                                 verbose_name='Plasmid',
                                 related_name='as_plasmid_in_cell',
                                 help_text='start typing for auto-completion')
    
    # rename to markers
    markers = models.ManyToManyField( 'DnaComponent', blank=True, null=True, 
                                      related_name='as_marker_in_cell',
                                      verbose_name='genomic markers',
                                      help_text='start typing ID or name ...')
    
        
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
        if self.markers.count():
            r += [ m for m in self.markers.all() if not m in r ]
        if self.plasmid:
            r += [ m for m in self.plasmid.allMarkers() if not m in r ]
        return r

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'Cell'
        ordering = ['displayId']


class ProteinComponent(Component, StatusMixinDna):
    """
    Description of a protein or protein fragment.
    """
   
    sequence = models.TextField( help_text='amino acid sequence', blank=True, 
                                 null=True )
    
    genbank = models.TextField( help_text='genbank file content', blank=True,
                                null=True )
    
    componentType = models.ForeignKey('ProteinComponentType', 
                                      verbose_name='Type',
                                      blank=False )

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'Protein'
        ordering = ['displayId']


class StatusMixinCommercial(models.Model, StatusMixin):
    
    STATUS_CHOICES = ( ('available', 'available'),
                       ('planning', 'planning'),
                       ('construction', 'ordered'),
                       ('abandoned', 'abandoned'))

    status = models.CharField( max_length=30, choices=STATUS_CHOICES, 
                               default='available')
    
    class Meta:
        abstract = True
    

class OligoComponent(Component, StatusMixinCommercial):
    """
    Description of DNA primer / oligo
    """
    PURE_CHOICES = (('desalting','desalting'),
                    ('RPC', 'Reverse-phase cartridge'),
                    ('HPLC','HPLC'),
                    ('PAGE','PAGE'),
                    ('unknown','unknown'))

    sequence = models.CharField( max_length=300,
                                 help_text="5' -> 3' nucleotide sequence", blank=True, 
                                 null=True )
    
    componentType = models.ForeignKey('OligoComponentType',
                                      verbose_name='Oligo Type',
                                      blank=False)
    
    templates = models.ManyToManyField('DnaComponent', blank=True, null=True,
                                       related_name='template_for_oligos',
                                       verbose_name='for DNA templates',
                                       help_text='start typing...')
    
    meltingTemp = models.IntegerField(u'Tm in \u00B0C', blank=True, null=True,
                                      help_text='melting temperature')
    

    purification = models.CharField( max_length=50, choices=PURE_CHOICES,
                                     blank=False)
    
    reversePrimers = models.ManyToManyField('self', 
                                            blank=True, null=True,
                                            symmetrical=True,
                                            help_text='select potential reverse primers')

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'Oligo'
        ordering = ['displayId']


class ChemicalComponent(Component, StatusMixinCommercial):
    """
    Description of a Chemical
    """
    
    componentType = models.ForeignKey('ChemicalType',
                                      verbose_name='Chemical Type',
                                      blank=False)

    cas = models.CharField( 'C.A.S.', max_length=20,
                            help_text="C.A.S. number", blank=True, 
                            null=True )
    
    
    class Meta:
        app_label = 'rotmic'
        verbose_name = 'Chemical'
        ordering = ['displayId']
