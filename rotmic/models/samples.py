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
from django.core.urlresolvers import reverse
from django.db.models import Q
import django.utils.html as html

from rotmic.models.components import UserMixin
from rotmic.models.storage import Container
import rotmic.utils.inheritance as I


class Sample( UserMixin ):
    """Base class for DNA, cell and protein samples."""

    displayId = models.CharField('Position', max_length=20,
                                 help_text='Label or well position.')

    container = models.ForeignKey(Container, related_name='samples')

    aliquotNr = models.PositiveIntegerField('Number of aliquots', 
                                            null=True, blank=True)

    STATUS_CHOICES = (('ok', 'ok'),
                      ('preparing', 'preparing'),
                      ('empty', 'empty'),
                      ('bad', 'bad'),
                      )
    
    status = models.CharField( max_length=30, choices=STATUS_CHOICES, 
                               default='ok', verbose_name='Status')
    
    comment = models.TextField('Comments', blank=True)

    preparedAt = models.DateField(default=datetime.now(), verbose_name="Prepared")
    
    source = models.CharField('External Source', blank=True, null=True, 
                              max_length=100,
                              help_text='external lab or company' )
    
    solvent = models.CharField('in Buffer/Medium', max_length=100, blank=True)

    concentration = models.FloatField('Concentration', null=True, blank=True)

    concentrationUnit = models.ForeignKey('Unit', 
                                          verbose_name='Conc. Unit',
                                          related_name='concUnit+',  ## supress back-reference
                                          null=True, blank=True,
                                          limit_choices_to = {'unitType': 'concentration'})    
    
    amount = models.FloatField('Amount', null=True, blank=True)
    amountUnit = models.ForeignKey('Unit', 
                                   verbose_name='Amount Unit',
                                   related_name='amountUnit+', ## suppress back-reference
                                   null=True, blank=True, 
                                   limit_choices_to = Q(unitType__in=['volume','number', 'mass'])
                                   )

    ## return child classes in queries using select_subclasses()
    objects = I.InheritanceManager()  

    def __unicode__(self):
        return u'%s \u2014 %s' % (self.container.displayId, self.displayId)
    
    def clean(self):
        """Prevent that parent class Samples are ever saved through admin."""
        from django.core.exceptions import ValidationError
        if self.__class__ is Sample:
            raise ValidationError('Cannot create generic samples without content.')        
    
    def save(self, *args, **kwargs):
        """Prevent parent class Sample saving at the django core level."""
        if self.__class__ is Sample:
            raise NotImplementedError('Attempt to create generic Sample instance.')
        super(Sample, self).save(*args, **kwargs)
    
    def commentText(self):
        """remove some formatting characters from text"""
        r = re.sub('--','', self.comment)
        r = re.sub('=','', r)
        r = re.sub('__','', r)
        return r
    commentText.short_description = 'description'
    
    def sameSamples(self):
        """
        Needs to be overriden!
        @return samples that have exactly the same content
        """
        return []
    
    def relatedSamples(self):
        """
        Samples that are related but not identical
        """
        return []

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
    
    def showVerbose(self):
        """display full chain location / rack / container / sample with links"""
        r = u''
        r += self.container.showVerbose() + ' / '
        
        title = 'Sample\n%s' % self.displayId
        if self.comment:
            title += '\n' + self.comment

        url = self.get_absolute_url()
        r += '<a href="%s" title="%s">%s</a>' % (url, title, self.displayId) 
        return html.mark_safe(r)
    
    showVerbose.allow_tags = True
    showVerbose.short_description = 'Sample'
    
    def showExtendedId(self):
        """Display Container -- Sample for table views"""
        r = u'%s : %s' % (self.container.displayId, self.displayId)

        title = self.comment
        url = self.get_absolute_url()
        return html.mark_safe('<a href="%s" title="%s">%s</a>' % (url, title, r))
    showExtendedId.allow_tags = True
    showExtendedId.short_description = u'Box : ID'
    
    def showContent(self):
        """Display sub-class-specific content for tables. Needs to be overridden"""
        return ''
    showContent.allow_tags = True
    showContent.short_description = u'Content'
    
    def showType(self):
        """Return type of sample (DNA, Cells, ...)"""
        r = getattr(self._meta, 'verbose_name', 'unknown type')
        r = r.split()[0]
        return r
    showType.short_description = 'Type'

    def showConcentration(self):
        conc = unicode(self.concentration or '')
        unit = unicode(self.concentrationUnit or '')
        return conc + ' '+ unit
    showConcentration.short_description = 'Concentration' 
    
    def showAmount(self):
        amount = unicode( self.amount or '' )
        unit   = unicode( self.amountUnit or '' )
        return amount + ' '+ unit
    showAmount.short_description = 'Amount' 
    
    class Meta:
        app_label = 'rotmic'
        verbose_name  = 'Sample'
        ordering = ['container', 'displayId']
   

class DnaSample( Sample ):
    """Samples linked to DnaComponent"""
    
    dna = models.ForeignKey('DnaComponent',
                            verbose_name = 'DNA construct',
                            related_name = 'dna_samples',
                            )

    def sameSamples(self):
        """
        @return samples that have exactly the same content
        """
        return DnaSample.objects.filter(dna=self.dna).exclude(id=self.id)
    
    def relatedSamples(self):
        """
        Samples that are related but not identical
        """
        return []

    def showContent(self):
        """Table display of linked insert or ''"""
        x = self.dna
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="%s">%s</a>- %s' \
                              % (url, x.comment, x.displayId, x.name))
    showContent.allow_tags = True
    showContent.short_description = 'DNA construct'
    

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'DNA Sample'
