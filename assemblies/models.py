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

from django.db import models
from django.utils.safestring import mark_safe
import django.utils.html as html
from django.contrib.auth.models import User

import rotmic.models as M

import rotmic.templatetags.rotmicfilters as F


class AssemblyProject(M.ReadonlyUrlMixin, M.ComponentBase):
    """Collection of DNA assembly reactions with shared parts."""

    STATUS_CHOICES = ( ('design', 'design'),
                       ('in progress', 'progress'),
                       ('completed', 'completed'),
                       ('cancelled', 'cancelled'))

    status = models.CharField( max_length=30, choices=STATUS_CHOICES, 
                               default='design')

    def showStatus(self):
        color = {u'completed': '088A08', # green
                 u'design': '808080', # grey
                 u'progress' : '0000FF', # blue
                 u'cancelled': 'B40404', # red
                 }
        r = '<span style="color: #%s;">%s</span>' %\
               (color.get(self.status, '000000'), self.get_status_display())
        return html.mark_safe(r)
    showStatus.allow_tags = True
    showStatus.short_description = 'Status'

    class Meta:
        app_label = 'assemblies'
        verbose_name = 'Assembly Project'


class AssemblyPart(M.Annotation):
    """
    Point to a particular region of a source DNA. Connects an assembly project
    to all potentially useful source parts. Can also specify a sequence without
    source (likely targetted for synthesis).
    """
    ## Annotion provides: bioStart, bioEnd, strand, preceedes
    
    component = models.ForeignKey(M.DnaComponent, blank=True, null=True,
                                  verbose_name='source construct',
                                  help_text='existing source DNA construct if any',
                                  related_name='assemblyParts')
    
    sequence = models.TextField(verbose_name='or specify sequence', 
                                help_text='or specify new nucleotide sequence', 
                                blank=True )
    
    assProject = models.ForeignKey(AssemblyProject, null=False, blank=False)
    
    def __unicode__(self):
        r = u'[%(component)s[%(start)i : %(end)i]'
        d = dict(component=self.component.__unicode__() if self.component else 'synthesis',
                 start=self.bioStart or 0,
                 end=self.bioEnd or -1)
        return r % d
    
    class Meta:
        app_label = 'assemblies'
        verbose_name = 'Assembly Part'


class AssemblyLink(models.Model):
    """
    Connect a single assembly product to the sequence of parts by which it is
    defined.
    """

    assembly = models.ForeignKey('Assembly', verbose_name='target assembly',
                                 null=False, blank=False, 
                                 related_name='partLinks')
    
    part = models.ForeignKey('AssemblyLink')

    position = models.SmallIntegerField()
    
    class Meta:
        app_label = 'assemblies'
        verbose_name = 'Assembly Link'
        ordering = ['assembly', 'position']


class Assembly(models.Model):
    """Capture information for a DNA assembly design"""
    
    displayId = models.CharField('ID', max_length=20, unique=True, 
                                 help_text='Unique identification')
    
    STATUS_CHOICES = ( ('design', 'design'),
                       ('ordered', 'ordered'),
                       ('assembly', 'assembly'),
                       ('screening','screening'),
                       ('sequencing', 'sequencing'),
                       ('completed', 'completed'),
                       ('cancelled', 'cancelled'))

    status = models.CharField( max_length=30, choices=STATUS_CHOICES, 
                               default='design')

    METHOD_CHOICES = ( ('gibson', 'Gibson assembly'),
                       ('golden', 'Golden Gate'),
                       ('classic', 'restriction/ligation'),
                       ('other', 'other') )
    
    method = models.CharField( max_length=30, choices=METHOD_CHOICES, 
                               default='gibson')
    
    preparedAt = models.DateField(default=datetime.now().date(), verbose_name="Prepared")
    
    preparedBy = models.ForeignKey(User, verbose_name="By")
    
   
    def showStatus(self):
        color = {u'completed': '088A08', # green
                 u'design': '808080', # grey
                 u'ordered' : '0000FF', # blue
                 u'assembly' : '0000FF', # blue
                 u'screening' : '0000FF', # blue
                 u'sequencing' : '0000FF', # blue
                 u'cancelled': 'B40404', # red
                 }
        r = '<span style="color: #%s;">%s</span>' %\
               (color.get(self.status, '000000'), self.get_status_display())
        return html.mark_safe(r)
    showStatus.allow_tags = True
    showStatus.short_description = 'Status'
    
    class Meta:
        app_label = 'assemblies'
        verbose_name = 'DNA Assembly'
        verbose_name_plural = 'DNA Assemblies'



##class DnaReaction(models.Model):
##    """
##    capture information for experimental preparation of a DNA fragment,
##    typically by PCR.
##    """
##    METHOD_CHOICES = ( ('PCR', 'PCR'),
##                       ('digest', 'restriction digest'),
##                       ('synthesis', 'gene synthesis'),
##                       ('other', 'other') )
##    
##    method = models.CharField( max_length=30, choices=METHOD_CHOICES, 
##                               default='PCR')
##
##    template = models.ForeignKey(DnaComponent, blank=True, null=True)
##    
##    product = models.ForeignKey(DnaComponent, blank=True, null=True)
##    
##    primer1 = models.ForeignKey(OligoComponent, blank=True, null=True)
##    primer2 = models.ForeignKey(OligoComponent, blank=True, null=True)
##    
##    flankLeft = models.CharField(max_length=100, blank=True)
##    flankRight = models.CharField(max_length=100, blank=True)
##
##    tm3 = models.FloatField(verbose_name="Tm3'")
##    tm  = models.FloatField(verbose_name='Tm full')
##    
##    overhangLeft = models.IntegerField()
##    overhangRight = models.IntegerField()
##    
##    class Meta:
##        app_label = 'rotmic'
##
##
