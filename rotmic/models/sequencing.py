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

from attachments import Attachment

class SequencingRun( Attachment ):
    """
    Representation of a single sequencing run -- basically wrapper for a trace
    file.
    """
    valid_extensions = ('abl','scf')
    parent_class = 'Component'

    sequencing = models.ForeignKey( 'Sequencing', related_name='runs' )
    
    primer = models.ForeignKey( 'OligoComponent', related_name='sequencingRun',
                                limit_choices_to={'brick_type__type_code__in':['G']},
                                blank=True, null=True )

    #sequence = customfields.TextModelField( 'sequence', rows=4, cols=40,
                                 #blank=True, null=True,
                                 #help_text='sequence extracted from trace file')

    class Meta:
        ordering = ('trace',)
        ## unique_together = (('trace',)) doesn't work
        


class Sequencing( models.Model, UserMixIn ):
    """
    Describe a sequencing result and analysis.
    Sequencing results are attached to Samples.
    """

    EVALUATION = (('confirmed','confirmed'), ('inconsistent','inconsistent'),
                  ('ambiguous','ambiguous'), ('','not analyzed') )

    sample = models.ForeignKey(DnaSample, related_name='sequencing', 
                               verbose_name='sequenced sample',
                               help_text='sample on which sequencing was performed')

    evaluation = models.CharField( 'evaluation', max_length=30,
                                   choices=EVALUATION, blank=True,
                                   default='',
                                   help_text='sequencing verdict with respect to target')

    comments = customfields.TextModelField( blank=True, rows=3)

    def __unicode__( self ):
        return u'_'.join([str(s) for s in [self.sample.label, self.created,
                                           self.id ]] )

    def get_absolute_url(self):
        """Define standard URL for object.get_absolute_url access in templates """
        return APP_URL+'/sequencing/%i/' % self.id

    class Meta:
        ordering = ('sample','id')

