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

from Bio import SeqIO
import StringIO

import django.forms as forms
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminDateWidget

import selectable.forms as sforms

from rotmic.utils.filefields import DocumentFormField
from rotmic.utils.multiFile import MultiFileField
import selectLookups as L
import rotmic.initialTypes as T

import rotmic.models as M


class TableUploadForm(forms.Form):
    """Form for uploading Excel Tables"""
    
    tableFile = DocumentFormField(label='Now, having read all that, please select an Excel file:',
                                  extensions=['xls','xlsx'])
    
    

class UploadFormBase(forms.Form):
    """Base class for bulk file upload forms"""
    
    ID_SEPARATORS = '[_\ \-\:;\.]+'

    def __init__(self, *arg, **kwarg):
        self.request = kwarg.pop('request')
        super(UploadFormBase, self).__init__(*arg, **kwarg)

    def normalize(self, s):
        """lower-case ID and remove leading zeros"""
        r = s.lower()
        r = re.sub('^0+', '', r, ) #remove leading zeros
        # remove leading zeros after letters
        ## \g puts the named group from the pattern match back into the string
        r = re.sub('(?P<letters>[a-z]+)0+(?P<number>[0-9]+)', '\g<letters>\g<number>', r)
        return r

    def add_error(self, field, msg):
        """
        This method exists in Form from django 1.7+ ; remove/rename after upgrade
        """
        self._errors[field] = self._errors.get( field, self.error_class([]) )
        if len( self._errors[field] ) < 3:
            self._errors[field].append(msg)
        elif len( self._errors[field] ) == 3:
            self._errors[field].append('...skipping further errors.')
 


class TracesUploadForm(UploadFormBase):
    """Form for attaching multiple sequencing trace files to selected DNA samples"""
    
    
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
                        help_text='Start typing container, sample or construct ID to restrict the choice.')
    
    matchBy = forms.ChoiceField(label='match by',
                                  choices=MATCHCHOICES,
                                  initial='s',
                                  widget=forms.RadioSelect,
                                  required=True,
                                  help_text="""Select how trace file names are matched to samples.
File names need to contain certain characters that separate the different IDs 
from each other and from the rest of the name. Allowed separating characters 
are: 

'_'(underscore), ' '(space), ':'(colon), ';'(semicolon), '-'(minus).

IDs are converted to lower case and leading zeros are removed to make the 
matching more robust. For example, let's assume you have a sample with ID 
'A01' which contains the DNA construct with ID 'sb0001'. If you select sample 
ID + construct ID matching, the following file names are all correct and will 
match the trace to this sample:

A1_sb0001_mysequencing.ab1 or 
a1-sb1-mysequencing.ab1 or 
A01:sb001_mysequencing.ab1
""")

    matchPrimer = forms.BooleanField(required=True, label='extract primer ID', 
                                    initial=True, 
                                    help_text="""Try to find a sequencing primer ID within the file name.
The trace file name may contain the ID of a sequencing primer. This ID has to
be an exact match (including capitalization/case and leading zeros) with the 
primer ID. The primer name does <em>not</em> work. The import will proceed 
even if there is no match, in which case the primer field is left empty for 
this trace.
""")

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
                                       help_text='User responsible for this sequencing\nStart typing user name to restrict choices.')
    
    comments = forms.CharField(label='Comments', required=False,
                               widget=forms.Textarea(attrs={'rows': 4,'cols': 80}),
                               help_text='This same comment will be put into every new sequencing record')

    def __init__(self, *arg, **kwarg):
        super(TracesUploadForm, self).__init__(*arg, **kwarg)

        ## Note: the 'self.fields['orderedBy'].initial =' syntax doesn't work with selectable fields
        self.initial['orderedBy'] = str(self.request.user.id)
        
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
        
    
    def findprimer(self, fname, primers=[]):
        """try identifying a sequencing primer ID in the filename"""
        for p in primers:
            if p.displayId in fname:
                return p
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

        seqprimers = M.OligoComponent.objects.filter(componentType=T.ocSequencing)
        
        for f in traces:
            
            if self.cleaned_data['matchPrimer']:
                primer = self.findprimer(f.name, seqprimers)

            run = M.SequencingRun(parent=r, f=f, description='multiple file upload',
                                  primer=primer)
            run.save()


class GenbankUploadForm(UploadFormBase):
    
    constructs = forms.ModelMultipleChoiceField(M.DnaComponent.objects.all(), 
                        cache_choices=False, 
                        required=True, 
                        widget=sforms.AutoComboboxSelectMultipleWidget(lookup_class=L.DnaLookup),
                        label='DNA constructs', 
                        initial=None, 
                        help_text='')
    
    genbank = MultiFileField(label='Genbank file(s)',
                           min_num=1,
                           extensions=['gb', 'gbk', 'genbank'],
                           help_text='Hold <CTRL> to select multiple files.')

    def clean_constructs(self):
        """
        Convert dna list into a dict indexed by the ID for matching.
        """
        data = self.cleaned_data['constructs']
        
        sdic = { self.normalize(s.displayId) : s for s in data }

        ## verify that all construct ids are unique with the current match
        if len(sdic) < len(data):
            raise forms.ValidationError(\
                'Sorry, there are constructs with (almost) identical IDs in the selected set. '+\
                'For example: SB0001 would be considered the same as sb01',
            code='invalid')
        
        return sdic
    
    def clean_genbank(self):
        """Convert uploaded file(s) into list of genbank record objects"""
        data = self.cleaned_data['genbank']
        
        r = []
        concat = ''
        try:
            ## BioPython genbank writing is sensitive to all kind of errors
            ## we therefore first concatenate all genbank files into one big string
            ## then parse it record by record which allows us to store
            ## the **original** genbank string along with the Biopython object
            for f in data:
                concat += ''.join(f.readlines()).strip()
            
            if concat:
                
                records = concat.split('//')[:-1]  ## skip '' split fragment after last //
                records = [ s + '//' for s in records ]
    
                for s in records:
                    f = StringIO.StringIO(s)
                    seqrecord = SeqIO.parse( f, 'gb' ).next()
    
                    seqrecord.original = s
                    r += [ seqrecord ]

        except StopIteration, why:
            raise forms.ValidationError('Empty or corrupted genbank file %s: %r' % \
                                        (f.name, why))
        except ValueError, why:
            raise forms.ValidationError('Error parsing genbank record from %s: %r' % \
                                        (f.name, why))
        except Exception, why:
            raise forms.ValidationError("Unknown error parsing %r: %r" % \
                                        (f, why))
            
        return r


    def findDna(self, name, sdic):

        frag = self.normalize( re.split(self.ID_SEPARATORS, name)[0] )

        if frag in sdic:
            return sdic[frag]
        
        self.add_error('genbank',\
            'Cannot match %s to any of the constructs.' % name +\
            'No construct can be identified by %s.' % frag )
        return None


    def mapGenbankToDna(self):
        """map given InMemoryFileUpload files to samples by name"""
        sdic = self.cleaned_data['constructs']
        records = self.cleaned_data['genbank']
        
        r = { s : None for s in sdic.values() }
        
        for gb in records:
            dna = self.findDna(gb.name, sdic)

            if dna:
                if r[dna] != None:
                    self.add_error('genbank',
                        'Duplicate entries: records %s and %s both match to the same construct %s' %\
                        (r[dna].name, gb.name, dna.displayId))

                r[dna] = gb

        if None in r.values():
            missing = [ x.displayId for x in r.keys() if r[x] == None ]
            self.add_error('genbank',
                           'Could not find record for the following constructs: '+\
                           ', '.join(missing))
        
        return r

    def replaceGenbank(self, dna, seqrecord):
        """
        extract genbank file from upload field
        @return True if this replaces an existing record, False otherwise
        """
        replaced = False
        try:
            dna.sequence = seqrecord.seq.tostring()
            dna.name = dna.name or seqrecord.name
            dna.description = dna.description or seqrecord.description

            replaced = bool(dna.genbank) ## empty? 
            
            dna.genbank = seqrecord.original ## custom variable created in clean_genbank           
            dna.save()
            
        except ValueError, why:
            msg = 'Error attaching genbank record: %r' % why
            self._errors['genbank'] = self.error_class([msg])

        return replaced
    
    
class GenbankProteinUploadForm(GenbankUploadForm):
    
    constructs = forms.ModelMultipleChoiceField(M.ProteinComponent.objects.all(), 
                    cache_choices=False, 
                    required=True, 
                    widget=sforms.AutoComboboxSelectMultipleWidget(lookup_class=L.ProteinLookup),
                    label='Protein constructs', 
                    initial=None, 
                    help_text='')
