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
import re

import django.forms as forms
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminDateWidget

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
    
    MATCHCHOICES = (('sample', 'sample ID (e.g. A01_comment.ab1)'), 
                    ('dna', 'construct ID (e.g. rg0011_comment.ab1)'),
                    ('containersample', 'container + sample ID (e.g. D12_A01_comment.ab1)'),
                    ('sampledna', 'sample ID + construct ID (e.g. A01_rg0011_comment.ab1)'))
    
    samples = forms.ModelMultipleChoiceField(M.DnaSample.objects.all(), 
                                             cache_choices=False, 
                                             required=True, 
                                             widget=None, 
                                             label='Samples', 
                                             initial=None, 
                                             help_text='Select the samples to which traces should be matched.')
    
    matchBy = forms.ChoiceField(label='match by',
                                  choices=MATCHCHOICES,
                                  initial='sample',
                                  widget=forms.RadioSelect,
                                  required=True,
                                  help_text='select how trace file names are matched to samples.')

    files = MultiFileField(label='Trace files:',
                           min_num=2,
                           extensions=['ab', 'abi', 'ab1', 'scf', 'phd'],
                           help_text='hold <CTRL> to select multiple files. Expected formats are: *.ab, *.abi, *.ab1,*.scf, *.phd')
    
    evaluation = forms.ChoiceField(label='evaluation',
                                   choices=M.Sequencing.EVALUATIONS, 
                                   initial='none',
                                   required=True,
                                   help_text='pre-set sequencing verdict with respect to target')
    
    orderedAt = forms.DateField(initial=datetime.now().date, label="ordered",
                                widget=AdminDateWidget)

    orderedBy = forms.ModelChoiceField(User.objects.all(), required=True, 
                                       label='By',
                                       help_text='User responsible for this sequencing')
    
    comments = forms.CharField(label='Comments', required=False,
                               widget=forms.Textarea(attrs={'rows': 4,'cols': 80}),
                               help_text='This same comment will be put into every new sequencing record')

    def __init__(self, *arg, **kwarg):
        self.request = kwarg.pop('request')
        super(TracesUploadForm, self).__init__(*arg, **kwarg)

        self.fields['orderedBy'].initial = self.request.user
        
    def normalize(self, s):
        """lower-case ID and remove leading zeros"""
        r = s.lower()
        r = re.sub('^0+', '', r, )
        return r

    def clean_samples(self):
        """
        Ensure unique sample IDs needed for file name matching
        Convert into a dict indexed by sample ID.
        """
        data = self.cleaned_data['samples']
        matchby = self.data['matchBy']
        
        if matchby == 'sample':
            sdic = { self.normalize(s.displayId) : s for s in data }
            
        elif matchby == 'dna':
            sdic = { s.content.displayId : s for s in data }
            
        elif matchby == 'containersample':
            sdic = { (self.normalize(s.container.displayId), self.normalize(s.displayId)) : s for s in data }

        elif matchby == 'sampledna':
            sdic = { (self.normalize(s.displayId), s.content.displayId) : s for s in data }
        
        else:
            raise forms.ValidationError('choice Error', code='error')

        ## verify that all sample ids are unique
        if len(sdic) < len(data):
            raise forms.ValidationError(\
                'Sorry, there are samples with identical IDs in the selected set.',
            code='invalid')
        
        return sdic

    def add_error(self, field, msg):
        """
        This method exists in Form from django 1.7+ ; remove/rename after upgrade
        """
        self._errors[field] = self._errors.get( field, self.error_class([]) )
        if len( self._errors[field] ) < 3:
            self._errors[field].append(msg)
        elif len( self._errors[field] ) == 3:
            self._errors[field].append('...skipping further errors.')
 
        
    def mapTracesToSamples(self, files):
        """map given InMemoryFileUpload files to samples by name"""
        sampledic = self.cleaned_data['samples']
        r = { s : [] for s in sampledic.values() }
        
        for f in files:
            frags = re.split('[\W_\-\:;]+', f.name) ## split at white space or -, _, :, ;
            frags = [ self.normalizeId(x) for x in frags ]

            if frags[0] in sampledic:
                s = sampledic[ frags[0] ]
                r[s] += [ f ]
            elif len(frags) > 1 and frags[1] in sampledic:
                s = sampledic[ frags[1] ]
                r[s] += [ f ]
            else:
                self.add_error('files',\
                    'Cannot match file %s to any of the selected samples.' % f.name +\
                    'There is no sample with ID %s.' % frags[0])
        
        return r