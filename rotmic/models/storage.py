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

class Location(UserMixin):
    """
    A location (fridge, freezer, shelf) where containers are stored
    """
    displayId = models.CharField('Location ID', max_length=20, unique=True, 
                                 help_text='Unique identifier')

    name = models.CharField('Name', max_length=200, blank=True, 
                            help_text='Informative name')

    temperature = models.FloatField('Temperature', default=25.0,
                                    blank=True, null=True,
                                    help_text= unichr(176) +'C')

    room = models.CharField('Room', max_length=20, blank=True,
                            help_text='room # if applicable')


    def __unicode__(self):
        r = unicode(self.displayId)
        if self.name:
            r += ' (%s)' % self.name
        return r

    def get_absolute_url(self):
        return reverse('admin:rotmic_location_readonly', args=(self.id,))
    
    def rackCount(self):
        return self.racks.count()
    
    def showRackCount(self):
        """Show number of Racks linked to pre-filtered Rack table"""
        url = reverse('admin:rotmic_rack_changelist')
        url += '?location=%s' % (self.id)
        r = '<a href="%s" title="jump to racks">%s</a>' % (url, self.rackCount())
        return html.mark_safe(r)
    showRackCount.allow_tags = True
    showRackCount.short_description = 'Racks'
        

    def containerCount(self):
        r = Container.objects.filter(rack__location=self).count()
        return r
    
    def showContainerCount(self):
        """Show number of containers linked to pre-filtered Container table"""
        url = reverse('admin:rotmic_container_changelist')
        url += '?location=%s' % (self.id)
        r = '<a href="%s" title="jump to containers">%s</a>' % (url, self.containerCount())
        return html.mark_safe(r)
    showContainerCount.allow_tags = True
    showContainerCount.short_description = 'Boxes'
       
    
    def sampleCount(self):
        from rotmic.models import Sample
        r = Sample.objects.filter(container__rack__location=self).count()
        return r

    def showSampleCount(self):
        """Show number of samples linked to pre-filtered Sample table"""
        url = reverse('admin:rotmic_sample_changelist')
        url += '?location=%s' % (self.displayId)
        r = '<a href="%s" title="jump to samples">%s</a>' % (url, self.sampleCount())
        return html.mark_safe(r)
    showSampleCount.allow_tags = True
    showSampleCount.short_description = 'Samples'


    def showVerbose(self):
        url = self.get_absolute_url()
        title = 'Location\n%s (%s)' % (self.displayId, self.name)
        if self.room:
            title += '\nin room %s' % self.room
        return html.mark_safe('<a href="%s" title="%s">%s</a>' \
                              % (url, title, self.displayId) )
    showVerbose.allow_tags = True
    showVerbose.short_description = 'Location'

    class Meta:
        app_label = 'rotmic'
        ordering = ('displayId',)
        verbose_name = 'Location'



class Rack(UserMixin):
    """
    A Rack (box) where containers are stored
    """
    displayId = models.CharField('Rack ID', max_length=20, unique=True, 
                                 help_text='Unique identifier')

    name = models.CharField('Name', max_length=100, blank=True, 
                            help_text='Informative name or label')

    location = models.ForeignKey( 'Location', blank=True, null=True,
                                  related_name='racks')
        
    def __unicode__(self):
        r = unicode(self.displayId)
        if self.name:
            r += ' (%s)' % self.name
        return r

    def get_absolute_url(self):
        return reverse('admin:rotmic_rack_readonly', args=(self.id,))

    def sampleCount(self):
        from rotmic.models import Sample
        r = Sample.objects.filter(container__rack=self).count()
        return r
    
    def showSampleCount(self):
        """Show number of samples linked to pre-filtered Sample table"""
        url = reverse('admin:rotmic_sample_changelist')
        url += '?location=%s&rack=%s' % (self.location.displayId, self.displayId)
        r = '<a href="%s" title="jump to samples">%s</a>' % (url, self.sampleCount())
        return html.mark_safe(r)
    showSampleCount.allow_tags = True
    showSampleCount.short_description = 'Samples'
    
    def containerCount(self):
        return self.containers.count()
    
    def showContainerCount(self):
        """Show number of containers linked to pre-filtered Container table"""
        url = reverse('admin:rotmic_container_changelist')
        url += '?location=%s&rack=%s' % (self.location.id, self.id)
        r = '<a href="%s" title="jump to containers">%s</a>' % (url, self.containerCount())
        return html.mark_safe(r)
    showContainerCount.allow_tags = True
    showContainerCount.short_description = 'Boxes'


    def showVerbose(self):
        r = u''
        if self.location:
            r += self.location.showVerbose() + ' / '
        
        title = 'Rack\n%s (%s)' % (self.displayId, self.name)

        url = self.get_absolute_url()
        r += '<a href="%s" title="%s">%s</a>' % (url, title, self.displayId) 
        return html.mark_safe(r)
    
    showVerbose.allow_tags = True
    showVerbose.short_description = 'Rack'

    class Meta:
        app_label = 'rotmic'   
        ordering = ('location__displayId', 'displayId',)
        verbose_name = 'Rack'


class Container( UserMixin ):
    """
    A container holding several physical samples of nucleic acids, proteins 
    or other stuff.
    """

    STORAGE_CONTAINER_TYPES= (
        ('96-well-plate', '96 well plate'),
        ('384-well-plate','384 well plate'),
        ('box', 'Freezer box'),
        ('other', 'other' ) )

    displayId = models.CharField('Box ID', max_length=20, unique=True,
                                 help_text='Unique ID')

    name = models.CharField('Name', max_length=100, blank=True,
                            help_text='Informative name or actual label')

    containerType = models.CharField('Type of container', max_length=30,
                                     default='box',
                                     choices=STORAGE_CONTAINER_TYPES )

    rack = models.ForeignKey(Rack, related_name='containers')
       
    #: optional long description
    comment = models.TextField( 'Detailed description', blank=True)

    def __unicode__(self):
        r = '%s / %s' % (self.rack.__unicode__(), unicode(self.displayId))

        if self.name:
            r += ' (%s)' % self.name
        return r

    def get_absolute_url(self):
        return reverse('admin:rotmic_container_readonly', args=(self.id,))

    def showVerbose(self):
        """show full chain Location / Rack / Container with URL links"""
        r = u''
        if self.rack:
            r += self.rack.showVerbose() + ' / '
        
        title = 'Container\n%s (%s)' % (self.displayId, self.name)
        if self.comment:
            title += '\n' + self.comment

        url = self.get_absolute_url()
        r += '<a href="%s" title="%s">%s</a>' % (url, title, self.displayId) 
        return html.mark_safe(r) 
    showVerbose.allow_tags = True
    showVerbose.short_description = 'Container'

    def showSampleCount(self):
        """Show number of samples linked to pre-filtered Sample table"""
        url = reverse('admin:rotmic_sample_changelist')
        url += '?location=%s&rack=%s&container=%s' % \
            (self.rack.location.displayId, self.rack.displayId, self.displayId)
        r = '<a href="%s" title="jump to samples">%s</a>' % (url, self.samples.count())
        return html.mark_safe(r)
    showSampleCount.allow_tags = True
    showSampleCount.short_description = 'Samples'

    class Meta:
        app_label = 'rotmic'   
        ordering = ('rack', 'displayId')
        verbose_name = 'Container'


