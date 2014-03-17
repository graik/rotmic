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
import os

import django.forms as forms
from django.core.exceptions import ValidationError
import django.db.models as models

class AttachmentForm(forms.ModelForm):
    """
    Catch missing files which can happen if object is resurrected by 
    reversion / History.
    """
        
    def clean_f(self):
        """Enforce existing file"""
        f = self.cleaned_data['f']
        if isinstance(f, models.fields.files.FieldFile) \
           and not os.path.exists( f.path ):

            fname = os.path.split( f.path )[-1]
            raise ValidationError('Attached file %s does not exist.' % fname, 
                                  code='file error')
        return f
    
