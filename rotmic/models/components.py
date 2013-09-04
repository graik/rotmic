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
import os

from django.db import models
from django.db.models.query import QuerySet as Q
from django.utils.safestring import mark_safe
from django.dispatch import receiver


from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from rotmic.utils.filefields import DocumentModelField


class UserMixin(models.Model):
    """
    Basic record keeping of registration dates and user.
    """

    registeredBy = models.ForeignKey(User, null=False, blank=False, 
                                related_name='%(class)s_created_by',
                                verbose_name='author')
    
    registeredAt = models.DateTimeField(default=datetime.now(), 
                                verbose_name="registered")
    
    def registrationDate(self):
        """extract date from date+time"""
        return self.registeredAt.date().isoformat()
    registrationDate.short_description = 'registered'
    
    def registrationTime(self):
        """extract time from date+time"""
        return self.registeredAt.time()
    registrationTime.short_description = 'at'

    class Meta:
        app_label = 'rotmic'        
        abstract = True



class Attachment(models.Model):
    """
    Handle a single uploaded file. Also manage the removal of this file if the
    attachment is deleted (which is not done automatically by django).
    """
    upload_to = 'attachments'
    valid_extensions = ()  ## disable extension checking
    parent_class = 'Component'
    
    f = DocumentModelField('file', 
                           upload_to=upload_to+'/'+parent_class,
                           extensions=valid_extensions,
                           blank=False, null=False)
    
    description = models.CharField(max_length=100, blank=True)

    parent = models.ForeignKey(parent_class, related_name='attachments')
    
    def __unicode__(self):
        return os.path.basename(self.f.name)

    class Meta:
        app_label = 'rotmic'
        abstract = True
    
# These two auto-delete files from filesystem when they are unneeded:
##@receiver(models.signals.post_delete, sender=Attachment)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.f:
        if os.path.isfile(instance.f.path):
            os.remove(instance.f.path)

##@receiver(models.signals.pre_save, sender=Attachment)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Attachment` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).f
    except sender.DoesNotExist:
        return False

    new_file = instance.f
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class ComponentAttachment(Attachment):
    parent_class = 'Component'
    
    class Meta:
        app_label='rotmic'
        abstract=False

models.signals.post_delete.connect(auto_delete_file_on_delete, 
                                   sender=ComponentAttachment)

models.signals.pre_save.connect(auto_delete_file_on_change, 
                                   sender=ComponentAttachment)



class Component(UserMixin):
    """
    Base class for cells, nucleic acids, proteins, and chemicals.
    Not shown to the user (currently) but the table exists and collects
    all fields that are common to all types of Components.
    
    See Meta.abstract
    """
    upload_to = 'attachments/Component'

    STATUS_CHOICES = ( ('available', 'available'),
                       ('planning', 'planning'),
                       ('under_construction', 'under construction'),
                       ('abandoned', 'abandoned'))

    displayId = models.CharField('ID', max_length=20, unique=True, 
        help_text='Unique identification')

    name = models.CharField('Name', max_length=200, blank=True, 
                            help_text='Descriptive name (e.g. "EGFP_pUC19")')

    comment = models.TextField('Description', blank=True)
    
    status = models.CharField( max_length=30, choices=STATUS_CHOICES, 
                               default='planning')
    
    def __unicode__(self):
        name = self.name or ''
        return u'%s - %s' % (self.displayId, name)


    class Meta:
        app_label = 'rotmic'
        abstract = False



class DnaComponent(Component):
    """
    Description of a stretch of DNA.
    """
   
    sequence = models.TextField( help_text='nucleotide sequence', blank=True, 
                                 null=True )      
    
    componentType = models.ForeignKey('DnaComponentType', 
                                           verbose_name='Type',
                                           related_name='Type',  blank=False )    
    
    insert = models.ForeignKey( 'self', blank=True, null=True, 
                                        related_name='Insert')
    
    vectorBackbone = models.ForeignKey( 'self', blank=True, null=True ,
                                        verbose_name='Vector Backbone')
    
    marker = models.ManyToManyField( 'self', blank=True, null=True, 
                                      related_name='Marker')
    
##    def related_dnaSamples(self):
##        """
##        """       
##        r = PlasmidSample.objects.filter(dnaComponent=self.id)
##        return r
    
##    def get_relative_url(self):
##        """
##        Define standard relative URL for object access in templates
##        """
##        return 'dnacomponent/%i/' % self.id
##    
    def get_absolute_url(self):
        """
        Define standard URL for object views
        see: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#reversing-admin-urls
        """
        from django.core.urlresolvers import reverse
        return reverse('admin:rotmic_dnacomponent_readonly', args=(self.id,))
    
    def get_absolute_url_edit(self):
        from django.core.urlresolvers import reverse
        return reverse('admin:rotmic_dnacomponent_change', args=(self.id,))
   

    def __unicode__(self):
        name = unicode(self.displayId + ' - ' + self.name)
        return name
          
    def save(self, *args, **kwargs):
        """
        Enforce optional fields depending on category.
        """
        category = self.componentType.category().name

        if category != 'Plasmid':
            self.insert = None
            self.vectorBackbone = None
        
##        ## this part somehow has no effect and leads to bugs.
##        if category not in ['Vector Backbone', 'Insert']:
##            self.marker = Q()
        
        return super(DnaComponent,self).save(*args, **kwargs)
            

    class Meta:
        app_label = 'rotmic'
        verbose_name = 'DNA construct'
        ordering = ['displayId']

