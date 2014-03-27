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

import django.forms as forms
from django.contrib.auth.models import User

from rotmic.utils.filefields import DocumentFormField
from rotmic.utils.multiFile import MultiFileField

import rotmic.models as M


class TableUploadForm(forms.Form):
    """Form for uploading table"""
    
    tableFile = DocumentFormField(label='Now, having read all that, please select an Excel file:',
                                  extensions=['xls','xlsx'])
    
    

class FilesUploadForm(forms.Form):
    """Form for uploading multiple files"""
    
    files = MultiFileField(label='Now, having read all that, please select files:',)
    

class TracesUploadForm(forms.Form):
    """Form for uploading multiple files"""
    
    files = MultiFileField(label='Trace files:',
                           extensions=['abl', 'scf'],
                           help_text='hold <CTRL> to select multiple files.')
    
    evaluation = forms.ChoiceField(label='evaluation',
                                   choices=M.Sequencing.EVALUATIONS, 
                                   initial='none',
                                   required=True,
                                   help_text='pre-set sequencing verdict with respect to target')
    
    orderedAt = forms.DateField(initial=datetime.now().date, label="ordered")

    orderedBy = forms.ModelChoiceField(User.objects.all(), required=True, 
                                       label='By',
                                       help_text='User responsible for this sequencing')
