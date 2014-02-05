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
"""Data models related to Vendors and product Ordering"""
from django.db import models
from django.core.urlresolvers import reverse

from rotmic.models.components import UserMixin

class Vendor(UserMixin):
    """Vendor (company) of a product"""

    name = models.CharField(max_length=30, unique=True, 
                            verbose_name='Vendor name', 
                            help_text='short descriptive name of this supplier')

    link = models.URLField(blank=True, 
                           help_text='URL Link to Vendor home page')

    phone = models.CharField(max_length=20, blank=True, 
                             verbose_name='Phone')

    email = models.CharField(max_length=30, blank=True, 
                             verbose_name='E-mail')

    contact = models.CharField(max_length=30, blank=True, 
                               verbose_name='Primary contact name')
    
    login = models.CharField(max_length=50, blank=True,
                               verbose_name='Account Login')

    password = models.CharField(max_length=30, blank=True,
                               verbose_name='Password')

    class Meta:
        ordering = ('name',)
        app_label = 'rotmic'        
        

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('admin:rotmic_vendor', args=(self.id,))

