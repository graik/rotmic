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
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse


class UserMixin(models.Model):
    """
    Basic record keeping of registration dates and user.
    """

    registeredBy = models.ForeignKey(User, null=False, blank=False, 
                                related_name='%(class)s_created_by',
                                verbose_name='registered by')
    
    registeredAt = models.DateTimeField(default=datetime.now(), 
                                verbose_name="registered")
    
    modifiedBy = models.ForeignKey(User, null=True, blank=True, 
                                related_name='%(class)s_modified_by',
                                verbose_name='modified by')
    
    modifiedAt = models.DateTimeField(default=datetime.now(), blank=True,
                                verbose_name="modified")
    
    
    def registrationDate(self):
        """extract date from date+time"""
        return self.registeredAt.date().isoformat()
    registrationDate.short_description = 'registered'
    
    def registrationTime(self):
        """extract time from date+time"""
        return self.registeredAt.time()
    registrationTime.short_description = 'at'

    def modificationDate(self):
        """extract date from date+time"""
        return self.modifiedAt.date().isoformat()
    modificationDate.short_description = 'modified'

    def modificationTime(self):
        """extract time from date+time"""
        return self.modifiedAt.time()
    modificationTime.short_description = 'at'

    class Meta:
        app_label = 'rotmic'        
        abstract = True


class ReadonlyUrlMixin:
    """URL methods for models that use the ViewFirstModelAdmin"""
    
    def get_absolute_url(self):
        """
        Define standard URL for object views
        see: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#reversing-admin-urls
        """
        classname = self.__class__.__name__.lower()
        return reverse('admin:rotmic_%s_readonly' % classname, args=(self.id,))
    
    def get_absolute_url_edit(self):
        """link to Editing Field"""
        classname = self.__class__.__name__.lower()
        return reverse('admin:rotmic_%s_change' % classname, args=(self.id,))
     