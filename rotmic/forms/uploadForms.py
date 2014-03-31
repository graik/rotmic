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

import selectable.forms as sforms

from rotmic.utils.filefields import DocumentFormField
from rotmic.utils.multiFile import MultiFileField
import selectLookups as L

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
    
    ID_SEPARATORS = '[_\ \-\:;]+'
    
    MATCHCHOICES = (('s', 'sample ID (e.g. A01_comment.ab1)'), 
                    ('s.dna', 'construct ID (e.g. rg0011_comment.ab1)'),
                    ('s.container:s', 'container + sample ID (e.g. D12_A01_comment.ab1)'),
                    ('s:s.dna', 'sample ID + construct ID (e.g. A01_rg0011_comment.ab1)'))
    
    samples = forms.ModelMultipleChoiceField(M.DnaSample.objects.all(), 
                        cache_choices=False, 
                        required=True, 
                        widget=sforms.AutoComboboxSelectMultipleWidget(lookup_class=L.DnaSampleLookup),
                        label='Samples', 
                        initial=None, 
                        help_text='Select the samples to which traces should be matched.')
    
    matchBy = forms.ChoiceField(label='match by',
                                  choices=MATCHCHOICES,
                                  initial='s',
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
                                       widget=sforms.AutoComboboxSelectWidget(lookup_class=L.UserLookup,
                                                       allow_new=False,
                                                       attrs={'size':15}),
                                       help_text='User responsible for this sequencing')
    
    comments = forms.CharField(label='Comments', required=False,
                               widget=forms.Textarea(attrs={'rows': 4,'cols': 80}),
                               help_text='This same comment will be put into every new sequencing record')

    def __init__(self, *arg, **kwarg):
        self.request = kwarg.pop('request')
        super(TracesUploadForm, self).__init__(*arg, **kwarg)

        ## Note: the 'self.fields['orderedBy'].initial =' syntax doesn't work with selectable fields
        self.initial['orderedBy'] = str(self.request.user.id)
        
    def normalize(self, s):
        """lower-case ID and remove leading zeros"""
        r = s.lower()
        r = re.sub('^0+', '', r, ) #remove leading zeros
        # remove leading zeros after letters
        ## \g puts the named group from the pattern match back into the string
        r = re.sub('(?P<letters>[a-z]+)0+(?P<number>[0-9]+)', '\g<letters>\g<number>', r)
        return r

    def _matchitems(self, fields, sample):
        """
        Extract displayIds from sample or sample sub-fields specified in fields.
        Normalize each ID to lower case and remove any leading zeros
        @return [str] - list of one or two IDs 
        """
        s = sample  ## fields are supposed to be 's' or 's.container' etc.
        r = [ eval(f+'.displayId') for f in fields ]
        r = [ self.normalize(s) for s in r ] 
        return tuple(r)

    def clean_samples(self):
        """
        Ensure unique sample IDs needed for file name matching
        Convert sample list into a dict indexed by the ID or IDs used for matching.
        """
        data = self.cleaned_data['samples']
        fields = self.data['matchBy'].split(':')
        
        sdic = { self._matchitems(fields, s) : s for s in data }

        ## verify that all sample ids are unique with the current match
        if len(sdic) < len(data):
            raise forms.ValidationError(\
                'Sorry, there are samples with identical IDs in the selected set. '+\
                'Select fewer samples or change the file name matching below.',
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
 

    def _findsample(self, fname, sdic):
        n_fields = len(sdic.keys()[0]) ## how many fragments are supposed to match?

        sep = self.ID_SEPARATORS
        frags = [ self.normalize(x) for x in re.split(sep, fname) ]

        searchfrags = tuple(frags[:n_fields]) ## should be first 1 or 2 fragments
        if searchfrags in sdic:
            return sdic[searchfrags]
        
        self.add_error('files',\
            'Cannot match %s to any of the samples.' % fname +\
            'No sample can be identified by %s.' % ' + '.join(searchfrags) )
        return None
        
    
    def mapTracesToSamples(self, files):
        """map given InMemoryFileUpload files to samples by name"""
        sdic = self.cleaned_data['samples']
        
        r = { s : [] for s in sdic.values() }
        
        for f in files:
            s = self._findsample(f.name, sdic)
            if s:
                r[s] += [f]

        if [] in r.values():
            missing = [ str(s) for s in r.keys() if r[s] == [] ]
            self.add_error('files',
                           'Could not find traces for the following samples: '+\
                           ', '.join(missing))
        
        return r
    
    def createSeq(self, sample, traces, **kwargs):
        """Create and save new sequencing and sequencingRun instances"""

        for key in ['orderedBy', 'orderedAt', 'evaluation', 'comments']:
            kwargs[key] = self.cleaned_data[key]
        
        kwargs['registeredBy'] = self.request.user
        kwargs['registeredAt'] = datetime.now()
        
        kwargs['comments'] += '\n(Created through trace file upload)'

        r = M.Sequencing(sample=sample, **kwargs)
        r.save()
        
        for t in traces:
            run = M.SequencingRun(parent=r, f=t, description='multiple file upload')
            run.save()

   