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
"""Models for attaching sequencing information to samples"""
from datetime import datetime

from django.db import models
from django.utils.safestring import mark_safe
import django.utils.html as html
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import django.contrib.staticfiles.templatetags.staticfiles as ST

import attachments as A
from .usermixin import UserMixin

class SequencingRun( A.Attachment ):
    """
    Representation of a single sequencing run -- basically wrapper for a trace
    file. Extends the custom attachment class; inheriting parameters f 
    (DocumentFileField) and description (CharField).
    """
    valid_extensions = ('abi', 'ab', 'ab1','scf', 'phd')
    parent_class = 'Sequencing'
    upload_to = ''
    
    parent = models.ForeignKey(parent_class, related_name='runs')
    
    primer = models.ForeignKey( 'OligoComponent', related_name='sequencingRun',
                                limit_choices_to={'componentType__name':'sequencing'},
                                blank=True, null=True )
    
    def __unicode__(self):
        return u'trace file %i' % self.pk

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

    EVALUATIONS = (('confirmed','confirmed'), ('inconsistent','inconsistent'),
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
                                   choices=EVALUATIONS, blank=False,
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

    def showEvaluation(self):
        color = {u'confirmed': '088A08', # green
                 u'inconsistent': 'B40404', # red
                 u'problems': 'FFA500', # orange
                 u'ambiguous' : '0000FF', # blue
                 u'none':  '000000', # black
                 }
        r = '<span style="color: #%s;">%s</span>' %\
                    (color.get(self.evaluation, '000000'), 
                     self.get_evaluation_display())
        return html.mark_safe( self.showEvaluationIcon() + ' ' + r)
    showEvaluation.allow_tags = True
    showEvaluation.short_description = 'Evaluation'
 
    def showEvaluationIcon(self):
        icons = {u'confirmed': 'icon_success.gif', # green
                 u'inconsistent': 'icon_error.gif', # red
                 u'problems': 'icon_alert.gif', # orange
                 u'ambiguous' : 'icon-unknown.gif', # blue
                 u'none':  'icon_clock.gif', # black
                 }
        f = ST.static('admin/img/' + icons.get(self.evaluation, ''))
        return html.mark_safe('<img src="%s" title="%s">' % \
                              (f, self.get_evaluation_display()))
    showEvaluationIcon.allow_tags = True
    showEvaluationIcon.short_description = 'Evaluation'

    class Meta:
        app_label='rotmic'
        verbose_name='Sequencing'
        ordering = ('sample','id')
        

