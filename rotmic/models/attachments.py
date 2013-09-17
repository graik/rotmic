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
"""Document / File attachment handling"""
import os

from django.dispatch import receiver
from django.db import models

from rotmic.utils.filefields import DocumentModelField


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
    
    parent = models.ForeignKey(parent_class, related_name='attachments')
    
    class Meta:
        app_label='rotmic'
        abstract=False
        verbose_name='Component Attachment'

models.signals.post_delete.connect(auto_delete_file_on_delete, 
                                   sender=ComponentAttachment)

models.signals.pre_save.connect(auto_delete_file_on_change, 
                                   sender=ComponentAttachment)


class SampleAttachment(Attachment):
    parent_class = 'Sample'
    
    parent = models.ForeignKey(parent_class, related_name='attachments')

    class Meta:
        app_label='rotmic'
        abstract=False
        verbose_name='Sample Attachment'

models.signals.post_delete.connect(auto_delete_file_on_delete, 
                                   sender=SampleAttachment)

models.signals.pre_save.connect(auto_delete_file_on_change, 
                                   sender=SampleAttachment)

