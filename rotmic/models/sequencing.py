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
from django.core.urlresolvers import reverse

import attachments as A
from .usermixin import UserMixin

class SequencingRun( A.Attachment ):
    """
    Representation of a single sequencing run -- basically wrapper for a trace
    file. Extends the custom attachment class; inheriting parameters f 
    (DocumentFileField) and description (CharField).
    """
    valid_extensions = ('abl','scf')
    parent_class = 'Sequencing'
    
    parent = models.ForeignKey(parent_class, related_name='runs')
    
    primer = models.ForeignKey( 'OligoComponent', related_name='sequencingRun',
                                limit_choices_to={'componentType__name':'sequencing'},
                                blank=True, null=True )
    
    def __unicode__(self):
        return u'trace file %i' % self.id

    class Meta:
        app_label='rotmic'
        abstract=False
        verbose_name='Sequencing Trace'

models.signals.post_delete.connect(A.auto_delete_file_on_delete, 
                                   sender=SequencingRun)

models.signals.pre_save.connect(A.auto_delete_file_on_change, 
                                   sender=SequencingRun)



class Sequencing( UserMixin ):
    """
    Describe a sequencing result and analysis.
    Sequencing results are attached to Samples.
    """

    EVALUATION = (('confirmed','confirmed'), ('inconsistent','inconsistent'),
                  ('ambiguous','ambiguous'), ('problems', 'seq. problems'), ('none','not analyzed') )

    sample = models.ForeignKey('DnaSample', related_name='sequencing', 
                               verbose_name='Sample',
                               help_text='sample on which sequencing was performed')

    orderedAt = models.DateField(default=datetime.now().date, verbose_name="ordered")

    orderedBy = models.ForeignKey(User, null=False, blank=False, 
                                related_name='%(class)s',
                                verbose_name='By',
                                help_text='User responsible for this sequencing')

    
    evaluation = models.CharField( 'evaluation', max_length=30,
                                   choices=EVALUATION, blank=False,
                                   default='none',
                                   help_text='sequencing verdict with respect to target')

    comments = models.TextField( blank=True )

    def __unicode__( self ):
        return u'%s-%s_%s_%i' % (self.sample.container.displayId, 
                                 self.sample.displayId, 
                                 self.registeredAt.strftime('%Y%m%d'),
                                 self.id)

    def get_absolute_url(self):
        """
        Define standard URL for object views
        see: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#reversing-admin-urls
        """
        classname = self.__class__.__name__.lower()
        return reverse('admin:rotmic_%s_change' % classname, args=(self.id,))

    class Meta:
        app_label='rotmic'
        verbose_name='Sequencing'
        ordering = ('sample','id')
        

