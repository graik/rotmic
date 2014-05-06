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

from .components import UserMixin, DnaComponent
from .componentTypes import DnaComponentType

class SequenceAnnotation(models.Model):
    """Base class for annotations between different kind of components"""

    bioStart = models.PositiveIntegerField('from position', blank=True, null=True,
                                        help_text='starting position (beginning with 1)')
    
    bioEnd = models.PositiveIntegerField('to position', blank=True, null=True,
                                      help_text='ending position (including)')
    
    strand = models.CharField('strand', max_length=1, choices=(('+',u'+'),('-',u'\u2013')), 
                              blank=False,
                              help_text='on strand (+...coding, -...anticoding)')
    
    hardLink = models.BooleanField('hard link sequence', default=False, null=False, 
                                   help_text='modify this sequence if target sequence changes')

    class Meta:
        app_label = 'rotmic'        
        abstract = True
    

class DnaAnnotation(SequenceAnnotation):
    """Annotation of sequence regions in Components"""

    parentComponent = models.ForeignKey(DnaComponent, blank=False,
                                        related_name='annotations')
    
    subComponent = models.ForeignKey(DnaComponent, verbose_name='Target DNA', blank=True, null=True )

    preceedes = models.ForeignKey('DnaAnnotation', verbose_name='Next', blank=True, null=True)

    class Meta:
        app_label = 'rotmic'        
        abstract = False