## Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013 - 2014 Raik Gruenberg

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
from django.contrib.auth.models import User

import Bio.SeqUtils.ProtParam as PP
import Bio.SeqUtils.MeltingTemp as TM
import Bio.SeqUtils as SeqUtils
from Bio.Seq import Seq
from Bio.Alphabet import generic_dna

from .usermixin import UserMixin, ReadonlyUrlMixin

import rotmic.templatetags.rotmicfilters as F
import rotmic.utils.inheritance as I
from rotmic.models.componentTypes import DnaComponentType

def _extractNumbers( queryset, pattern ):
    matches = [ pattern.match( o.displayId ) for o in queryset ]
    numbers = [ int(x.groups()[0]) for x in matches if x is not None ]
    numbers.sort()
    return numbers    


class Component(UserMixin, ReadonlyUrlMixin):
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
    
    
    authors = models.ManyToManyField(User, null=False, blank=False, 
                                related_name='%(class)ss_authored',
                                verbose_name='Authors')
    
    
    projects = models.ManyToManyField('Project', blank=True, null=True,
                                      verbose_name='Projects',
                                     related_name='components',   ## end with + to suppress reverse relationship
                                     )

    description = models.TextField('Description', blank=True,
                help_text='You can format your text and include links. See: <a href="http://daringfireball.net/projects/markdown/basics">Markdown Quick Reference</a>')
    
    ## return child classes in queries using select_subclasses()
    objects = I.InheritanceManager()  

    @property
    def samples(self):
        """
        return subtype-specific django RelatedManager pointing to all samples
        for this specific component.
        Needs to be overriden
        """
        raise NotImplemented, 'samples method must be implemented by sub-classes.'

    def __unicode__(self):
        name = self.name or ''
        return u'%s (%s)' % (self.displayId, name)

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
    
    @staticmethod
    def nextAvailableId(user, prefix=None, category_id=None):
        """
        determine the next free ID for given user and component category.
        
        category_id - int, pk of ComponentType instance selected in Category field
        This parameter is ignored in this default implementation.
        """
        prefix = prefix or user.profile.prefix
        objects = Component.objects.filter( displayId__startswith=prefix )

        if objects.count() == 0:
            return '%s%04i' % (prefix, 1)

        pattern = re.compile(prefix+'([0-9]+)')
        numbers = _extractNumbers( objects, pattern ) or [0]
        
        return '%s%04i' % (prefix, numbers[-1]+1)
        

    class Meta:
        app_label = 'rotmic'
        abstract = False
        ordering = ['displayId']


class StatusMixinDna(models.Model):
    
    STATUS_CHOICES = ( ('available', 'available'),
                       ('planning', 'planning'),
                       ('construction', 'construction'),
                       ('abandoned', 'abandoned'))

    status = models.CharField( max_length=30, choices=STATUS_CHOICES, 
                               default='planning')
    
    def showStatus(self):
        color = {u'available': '088A08', # green
                 u'planning': '808080', # grey
                 u'construction' : '0000FF', # blue
                 u'abandoned': 'B40404', # red
                 }
        r = '<span style="color: #%s;">%s</span>' %\
               (color.get(self.status, '000000'), self.get_status_display())
        return html.mark_safe(r)
    showStatus.allow_tags = True
    showStatus.short_description = 'Status'
    
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
                                      blank=False,
                                      on_delete=models.PROTECT)    
    
    insert = models.ForeignKey( 'self', blank=True, null=True,
                                related_name='as_insert_in_dna',
                                help_text='start typing ID or name of DNA <b>Fragment</b>')
    
    vectorBackbone = models.ForeignKey( 'self', blank=True, null=True ,
                                        verbose_name='Vector Backbone',
                                        related_name='as_vector_in_plasmid',
                                        help_text='start typing ID or name of base vector',
                                        on_delete=models.PROTECT)  ## prevent deletion of vectorBB in use
    
    markers = models.ManyToManyField( 'self', blank=True, null=True, 
                                     symmetrical=False,
                                     related_name='as_marker_in_dna',   ## end with + to suppress reverse relationship
                                     verbose_name='Selection markers',
                                     help_text='start typing ID or name of marker')
    
    translatesTo = models.ForeignKey('ProteinComponent',
                                     verbose_name='Translates to',
                                     related_name='codingSequences',
                                     help_text='start typing ID or name of encoded protein',
                                     null=True, blank=True,
                                     on_delete=models.SET_NULL)  ## do not remove DC if protein is deleted
    
    
    @property
    def samples(self):
        """
        return subtype-specific django RelatedManager pointing to all samples
        for this specific component.
        """
        return self.dna_samples
    
    @property
    def cellSamples(self):
        """Cell samples containing this DNA construct"""
        from . import CellSample

        sample_ids = self.as_plasmid_in_cell.values_list('cell_samples', flat=True)
        sample_ids = [ i for i in sample_ids if i ] ## filter out None

        cellsamples = CellSample.objects.filter(id__in=sample_ids)
        return cellsamples

    @property
    def allSamples(self):
        """
        DNA and cell samples for this construct.
        """
        dnasamples = self.dna_samples.all()
        return list(dnasamples) + list(self.cellSamples)

    @staticmethod
    def nextAvailableId(user, prefix=None, category_id=None):
        """
        determine the next free ID for given user and component category.
        category_id - int, pk of ComponentType instance selected in Category field
        """
        import rotmic.initialTypes as T  ## local import to avoid recursion
        
        cat = DnaComponentType.objects.get(id=category_id)
        
        default_prefix = user.profile.dcPrefix or user.profile.prefix

        if cat.id in [T.dcMarker.id, T.dcVectorBB.id]:
            default_prefix += cat.name.lower()[0] 
        
        prefix = prefix or default_prefix
        
        return Component.nextAvailableId(user, prefix)

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
        
##        if category != 'Fragment':
##            self.translatesTo = None
        
        return super(DnaComponent,self).save(*args, **kwargs)


    def allMarkers( self ):
        """
        @return: QuerySet(DnaComponent)
        All markers contained in this DC directly or within a linked
        insert or vector backbone.
        Note: using queryset combination and limiting count() etc is speeding
        up this code
        """
        r = self.markers.all()  ## queryset
        if self.vectorBackbone:
            r = r | self.vectorBackbone.allMarkers() ## combine querysets
        if self.insert:
            r = r | self.insert.allMarkers()
        return r
    
    def allProteins( self ):
        """
        All proteins encoded by this DNA or its markers / insert / vector
        @return [ProteinComponent]
        """
        r = [ self.translatesTo ] if self.translatesTo else []

        for m in self.markers.all():
            r += m.allProteins()
        if self.insert:
            r += self.insert.allProteins()
        if self.vectorBackbone:
            r += self.vectorBackbone.allProteins()

        return r

    def seq2aa(self):
        """translate nucleotide to protein sequence"""
        r = ''
        try:
            dna = Seq(self.sequence, generic_dna)
            r = dna.translate()
        except ValueError, why:
            r = why
        return r

    def length( self ):
        """@return int, nt count"""
        if not self.sequence:
            return 0
        return len(self.sequence)
    
    def gccontent(self):
        """@return float, GC content of sequence in %"""
        r = 0.0
        try:
            r = SeqUtils.GC(self.sequence)
        except:
            pass
        return round(r, 0)

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
                                      blank=False,
                                      on_delete=models.PROTECT)    
    
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
            

    @property
    def samples(self):
        """
        return subtype-specific django RelatedManager pointing to all samples
        for this specific component.
        """
        return self.cell_samples

    @staticmethod
    def nextAvailableId(user, prefix=None, category_id=None):
        """
        determine the next free ID for given user and (ignored) component category.
        """
        default_prefix = user.profile.ccPrefix or user.profile.prefix + 'c'
        prefix = prefix or default_prefix
        
        return Component.nextAvailableId(user, prefix)

    def allMarkers( self ):
        """
        @return: [DnaComponent]
        All markers contained in this cell directly or within a linked
        plasmid.
        """
        r = self.markers.all() ## potentially empty queryset
        if self.plasmid:
            r = r | self.plasmid.allMarkers()  ## combine queryset, more efficient than [] + []
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
                                      blank=False,
                                      on_delete=models.PROTECT)

    @property
    def samples(self):
        """
        return subtype-specific django RelatedManager pointing to all samples
        for this specific component.
        """
        return self.protein_samples

    @staticmethod
    def nextAvailableId(user, prefix=None, category_id=None):
        """
        determine the next free ID for given user and component category.
        category_id is ignored
        """
        default_prefix = user.profile.pcPrefix or user.profile.prefix + 'p'
        prefix = prefix or default_prefix
        
        return Component.nextAvailableId(user, prefix)

    def length( self ):
        """@return int, amino acid count"""
        if not self.sequence:
            return 0
        return len(self.sequence)
    
    def mass( self ):
        """@return float, ProtParam molecular weight"""
        if not self.sequence:
            return 0.0
        try:
            return PP.ProteinAnalysis(self.sequence).molecular_weight()
        except:
            return 0.0
    
    def isoelectric( self ):
        """@return float, ProtParam iso-electric point"""
        if not self.sequence:
            return 0.0
        try:
            r = PP.ProteinAnalysis(self.sequence).isoelectric_point()
            return round(r, 2)
        except:
            return 0.0
        

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'Protein'
        ordering = ['displayId']


class StatusMixinCommercial(models.Model):
    
    STATUS_CHOICES = ( ('available', 'available'),
                       ('planning', 'planning'),
                       ('construction', 'ordered'),
                       ('abandoned', 'abandoned'))

    status = models.CharField( max_length=30, choices=STATUS_CHOICES, 
                               default='available')
    
    def showStatus(self):
        color = {u'available': '088A08', # green
                 u'planning': '808080', # grey
                 u'construction' : '0000FF', # blue
                 u'abandoned': 'B40404', # red
                 }
        r = '<span style="color: #%s;">%s</span>' %\
               (color.get(self.status, '000000'), self.get_status_display())
        return html.mark_safe(r)
    showStatus.allow_tags = True
    showStatus.short_description = 'Status'

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
                                      blank=False,
                                      on_delete=models.PROTECT)
    
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

    @property
    def samples(self):
        """
        return subtype-specific django RelatedManager pointing to all samples
        for this specific component.
        """
        return self.oligo_samples
    
    @staticmethod
    def nextAvailableId(user, prefix=None, category_id=None):
        """
        determine the next free ID for given user and component category.
        category_id -- ignored
        """
        default_prefix = user.profile.ocPrefix or user.profile.prefix + 'o'
        prefix = prefix or default_prefix
        
        return Component.nextAvailableId(user, prefix)

    def tm_nn(self, dnaconc=500, saltconc=50):
        """
        dnaconc - float, [DNA] nM
        saltconc - float, [salt] mM
        @return float, nearest neighbore dna/dna melting temperature
        """
        if not self.sequence:
            return 0
        r = TM.Tm_staluc(self.sequence, dnac=dnaconc, saltc=saltconc)
        return round(r,1)
        

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
                                      blank=False,
                                      on_delete=models.PROTECT)

    cas = models.CharField( 'C.A.S.', max_length=20,
                            help_text="C.A.S. number", blank=True, 
                            null=True )
    
    
    @property
    def samples(self):
        """
        return subtype-specific django RelatedManager pointing to all samples
        for this specific component.
        """
        return self.chemical_samples

    @staticmethod
    def nextAvailableId(user, prefix=None, category_id=None):
        """
        determine the next free ID for given user and component category.
        category_id is ignored
        """
        default_prefix = user.profile.chPrefix or user.profile.prefix + 'r'
        prefix = prefix or default_prefix
        
        return Component.nextAvailableId(user, prefix)

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'Chemical'
        ordering = ['displayId']
