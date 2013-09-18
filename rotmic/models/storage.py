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


    def child_racks( self ):
        r = Rack.objects.filter( location=self.id )
        return r    

    def __unicode__(self):
        r = unicode(self.displayId)
        if self.room:
            r += ' (R. %s)' % self.room
        return r

    def get_absolute_url(self):
        return reverse('admin:rotmic_location_change', args=(self.id,))

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

    location = models.ForeignKey( 'Location', blank=True, null=True )
        
    def __unicode__(self):
        r = unicode(self.displayId)
        if self.name:
            r += ' (%s)' % self.name
        return r

    def get_absolute_url(self):
        return reverse('admin:rotmic_rack_change', args=(self.id,))

    def child_containers( self ):
        r = Container.objects.filter( rack=self.id )
        return r    

    class Meta:
        app_label = 'rotmic'   
        ordering = ('location__displayId', 'displayId',)
        unique_together = ('displayId', 'location')


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
                                 help_text='Unique identifier')

    name = models.CharField('Name', max_length=100, blank=True,
                            help_text='Informative name or actual label')

    containerType = models.CharField('Type of container', max_length=30,
                                     default='box',
                                     choices=STORAGE_CONTAINER_TYPES )

    rack = models.ForeignKey(Rack)
       
    #: optional long description
    comment = models.TextField( 'Detailed description', blank=True)

    def __unicode__(self):
        r = unicode(self.displayId)
        if self.name:
            r += ' (%s)' % self.name
        return r

    def get_absolute_url(self):
        return reverse('admin:rotmic_container_change', args=(self.id,))


    class Meta:
        app_label = 'rotmic'   
        ordering = ('displayId',)
        unique_together = ('displayId', 'rack')


