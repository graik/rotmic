## Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013-2014 Raik Gruenberg

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

from .components import UserMixin, Component
from .componentTypes import DnaComponentType

class Annotation(models.Model):
    """Base class for part annotations (links) between different kind of components"""

    bioStart = models.PositiveIntegerField('from', blank=True, null=True,
                                        help_text='starting position (beginning with 1)')
    
    bioEnd = models.PositiveIntegerField('to', blank=True, null=True,
                                      help_text='ending position (including)')
    
    strand = models.CharField('strand', max_length=1, choices=(('+',u'+'),('-',u'\u2013')), 
                              blank=False, default='+',
                              help_text='on strand (+...coding, -...anticoding)')
    
    @property
    def target(self):
        """@return properly type-cast parent component to which this annotation is assigned"""
        raise NotImplemented
    
    class Meta:
        app_label = 'rotmic'        
        abstract = True
    

class SequenceFeature(Annotation):
    """
    Purely descriptive annotation without linking to any other component,
    typically coming from genbank entry.
    """
    
    component = models.ForeignKey(Component, verbose_name='target construct',
                                  blank=False,
                               related_name='sequenceFeatures')
    
    name = models.CharField('Name', max_length=200, blank=False, 
                            help_text='short descriptive name')
    
    featureType = models.CharField('Type', max_length=200, blank=True, 
                                   help_text='genbank feature type')
    
    description = models.TextField('Description', blank=True,
                                   help_text='more detailed description')

    class Meta:
        app_label = 'rotmic'        
        abstract = False


class SequenceLink(Annotation):
    """Link a sequence region to another Component"""

    component = models.ForeignKey(Component, verbose_name='target construct',
                                  blank=False,
                                  related_name='sequenceLinks')
    
    subComponent = models.ForeignKey(Component, verbose_name='source part',
                                     related_name='linkedVia',
                                     blank=True, null=True )

    hardLink = models.BooleanField('hard link sequence', default=False, null=False, 
                                   help_text='modify target sequence if source sequence changes')

    class Meta:
        app_label = 'rotmic'        
        abstract = False