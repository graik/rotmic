from django.db import models
import django.forms as forms
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from django.contrib.admin import widgets as adminwidgets

import re
from os.path import splitext


class DocumentFormField(forms.FileField):
    """
    Validate a file against a set of file endings and size
    See also: http://www.neverfriday.com/sweetfriday/2008/09/-a-long-time-ago.html
    """
    widget = adminwidgets.AdminFileWidget
    extensions = ('pdf','doc','txt','rtf','fasta','abl')
    default_max_size = 5e6
    valid_content_types = ('text/html', 'text/plain', 'text/rtf',
                           'text/xml', 'application/msword',
                           'application/rtf', 'application/pdf')
   
   
    def __init__(self, *args, **kw):
        """
        @param extensions: [str], allowed file extensions
        @param size: int, maximum file size
        """
        self.extensions = kw.pop( 'extensions', self.extensions )
        self.size = kw.pop('size', self.default_max_size )
        
        super(DocumentFormField, self).__init__( *args, **kw )
        
        
    def validate(self, value):
        """Enforce file ending and file size"""
      
        super(DocumentFormField, self).validate(value)
        
        if value is None:  ## non-required empty field
            return
        
        try:
            ext = value.name.split('.')[-1].lower()  
        except:
            raise forms.ValidationError('Invalid file name %s' \
                                        % value.name,
                                        code='invalid file',
                                        )

        if self.extensions and not ext in self.extensions:
            raise forms.ValidationError(
                'Invalid file extension %s. Allowed are %r' \
                % (ext, self.extensions),
                code='invalid file'
            )

        if value.size > self.size:
            raise forms.ValidationError(
                'File is too big (%i > %i)' % (value.size,self.size),
                code='invalid file')

       
    
class DocumentModelField( models.FileField ):
    """FileField validated against size and ending"""
    
    def __init__(self, *args, **kw):
        """
        @param extensions: [str], allowed file extensions
        @param size: int, maximum file size
        """
        self.extensions = kw.pop( 'extensions', 
                                  DocumentFormField.extensions )
        self.size = kw.pop('size', DocumentFormField.default_max_size )
        
        super(DocumentModelField, self).__init__( *args, **kw )

    def formfield(self, **kwargs):
        defaults = {'form_class': DocumentFormField}
        defaults.update(kwargs)
        
        defaults.update( {'extensions':self.extensions, 'size':self.size} )

        return super(DocumentModelField, self).formfield(**defaults)
    
from south.modelsinspector import add_introspection_rules
add_introspection_rules([
    (
        [DocumentModelField], # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
            "extensions": ["extensions", {"default": DocumentFormField.extensions}],
            'size': ['size', {'default':DocumentFormField.default_max_size}]
        },
    ),
], ["^rotmic\.utils\.filefields\.DocumentModelField"])
       
