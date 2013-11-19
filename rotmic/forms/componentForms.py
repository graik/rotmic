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
import os, re, datetime, StringIO

from Bio import SeqIO

import django.forms as forms
import django.db.models as models
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

import rotmic.models as M

import rotmic.initialTypes as T
import rotmic.initialUnits as U

import rotmic.utils.sequtils as sequtils
from rotmic.utils.filefields import DocumentFormField

import selectLookups as L
import selectable.forms as sforms

class CleaningMixIn:
    """Mixin to enforce a certain displayID format"""
    
    ex_id = re.compile('[a-z]{1,6}[0-9]{4}[a-z]{0,1}')
    msg_id = 'ID must have format a[bcdef]0123[a].'  ## for human-readable messages
    
    def clean_displayId(self):
        """enforce letter-digit displayId: a(bcdef)0123(a)"""
        r = self.cleaned_data['displayId']
        r = r.strip()

        if not self.ex_id.match(r):
            raise ValidationError(self.msg_id)
        return r
        

class DnaComponentForm(forms.ModelForm, CleaningMixIn):
    """Customized Form for DnaComponent (DNA construct) add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            widget=L.SilentSelectWidget,
                            queryset=M.DnaComponentType.objects.filter(subTypeOf=None),
                            required=True, 
                            empty_label=None,
                            initial=T.dcPlasmid)
    
    ## genbankFile upload into textfield 'genbank' is handled by ModelAdmin.save_model
    genbankFile = DocumentFormField(label='GenBank file', required=False,
                                    help_text='This will replace the current sequence.',
                                     extensions=['gbk','gb','genebank'])
    

    def __init__(self, *args, **kwargs):
        super(DnaComponentForm, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)
        
        self.fields['markers'].help_text = 'Start typing ID or name...'

        o = kwargs.get('instance', None)
        if o:
            self.fields['componentCategory'].initial = o.componentType.subTypeOf
    
    def clean_sequence(self):
        """Enforce DNA sequence."""
        r = self.cleaned_data['sequence']
        if not r:
            return r

        r = sequtils.cleanseq( r )
        
        if not sequtils.isdna( r ):
            raise ValidationError('This is not a DNA sequence.', code='invalid')        
        return r
    
    def clean_componentCategory(self):
        r = self.cleaned_data['componentCategory']

        if self.instance and self.instance.id and ('componentType' in self.changed_data):
            assert( isinstance(r, M.DnaComponentType) )
            msg = 'Cannot change category: '

            if r.id != T.dcVectorBB and self.instance.as_vector_in_plasmid.count():
                raise ValidationError(msg + 'This construct is in use as a vector backbone.')
            
            if not r.id in [T.dcFragment.id, T.dcMarker.id] and \
               self.instance.as_insert_in_dna.count():
                raise ValidationError(msg + 'This construct in use as an insert.')
                
            if r.id != T.dcMarker and (self.instance.as_marker_in_cell.count() \
                                       or self.instance.as_marker_in_dna.count() ):
                raise ValidationError(msg + 'This construct is in use as a marker.')
        
            if r.id != T.dcPlasmid and self.instance.as_plasmid_in_cell.count():
                raise ValidationError(msg + 'This construct is in use as a plasmid.')
        return r
    
    
    def clean_insert(self):
        """
        Enforce DC of type 'Fragment' or 'Marker'
        This should not strictly be needed as the dialogue is only populated
        with correct types of DnaComponents but the type of an existing
        construct may later be change.
        """
        r = self.cleaned_data['insert']
        if not r:
            return r
        
        assert( isinstance(r, M.DnaComponent) )
        if not r.componentType.category().id in [T.dcFragment.id, T.dcMarker.id]:
            raise ValidationError('Constructs of category %s are not allowed as an insert.'\
                                  % r.componentType.category().name )
        return r

    def clean_vectorBackbone(self):
        """
        Enforce DC of type 'VectorBackbone'. 
        This should not strictly be needed as the dialogue is only populated
        with correct types of DnaComponents but the type of an existing
        construct may later be change.
        """
        r = self.cleaned_data['vectorBackbone']
        if not r:
            return r
        
        assert( isinstance(r, M.DnaComponent) )
        if not r.componentType.category().id == T.dcVectorBB.id:  ## for some reason "is" doesn't work
            raise ValidationError('Given construct is not a vector backbone.')
        return r
    
    def clean_markers(self):
        """Enforce all markers to be really classified as marker"""
        r = self.cleaned_data['markers']
        if not r.count():
            return r
        
        for m in r:
            assert( isinstance(m, M.DnaComponent))
            if not m.componentType.category().id == T.dcMarker.id:
                raise ValidationError('%s is not a marker.' % m.__unicode__() )
        return r
        

    def clean(self):
        """
        Remove values for hidden fields, which might have been set before final
        category was selected.
        Note: this is also partly enforced by the DnaComponent.save method.
        """
        data = super(DnaComponentForm, self).clean()
        category = data.get('componentCategory', None) 

        if category and (category != T.dcPlasmid):
            data['insert'] = None
            data['vectorBackbone'] = None
        
        if category and (category not in [T.dcVectorBB, T.dcFragment] and 'markers' in data):
            data['markers'] = QuerySet()
            
        ## validate that a vector backbone is given if category == Plasmid
        if category == T.dcPlasmid and not data.get('vectorBackbone',None):
            msg = u'Vector Backbone is required for Plasmids.'
            self._errors['vectorBackbone'] = self.error_class([msg])
        
        ## extract genbank file from upload field
        try:
            if data.get('genbankFile', None):
                if self.errors:
                    msg = 'Please correct the other error(s) and upload the file again.'
                    self._errors['genbankFile'] = self.error_class([msg])
                else:
                    o = self.instance
                    upload = data['genbankFile']
                    o.genbank = ''.join(upload.readlines())
    
                    f = StringIO.StringIO( o.genbank )
                    seqrecord = SeqIO.parse( f, 'gb' ).next()
                    data['sequence'] = seqrecord.seq.tostring()
                    if not data.get('name', ''):
                        data['name'] = seqrecord.name
                    if not data.get('description', ''):
                        data['description'] = seqrecord.description
        except StopIteration:
            msg = 'Empty or corrupted genbank file'
            self._errors['genbankFile'] = self.error_class([msg])
        except ValueError, why:
            msg = 'Error reading genbank file: %r' % why
            self._errors['genbankFile'] = self.error_class([msg])

        return data
      
                
    class Meta:
        model = M.DnaComponent

        widgets = {  ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),

            'sequence': forms.Textarea(attrs={'cols': 100, 'rows': 4,
                                               'style':'font-family:monospace'}), 
            'description' : forms.Textarea(attrs={'cols': 100, 'rows': 10,
                                              'style':'font-family:monospace'}),

            'insert' : sforms.AutoComboboxSelectWidget(lookup_class=L.InsertLookup, 
                                                       allow_new=False,
                                                       attrs={'size':35}),
            'vectorBackbone' : sforms.AutoComboboxSelectWidget(lookup_class=L.VectorLookup, allow_new=False),

            'markers' : L.FixedSelectMultipleWidget(lookup_class=L.MarkerLookup)
        }


class CellComponentForm(forms.ModelForm, CleaningMixIn):
    """Customized Form for DnaComponent (DNA construct) add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Species',
                            widget=L.SilentSelectWidget,
                            queryset=M.CellComponentType.objects.filter(subTypeOf=None),
                            required=True, 
                            empty_label=None,
                            initial=T.ccEcoli)
    

    def __init__(self, *args, **kwargs):
        super(CellComponentForm, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)

        o = kwargs.get('instance', None)
        if o:
            self.fields['componentCategory'].initial = o.componentType.subTypeOf
        

    def clean_plasmid(self):
        """
        Enforce DC of type 'Plasmid'. 
        This should not strictly be needed as the dialogue is only populated
        with correct types of DnaComponents but the type of an existing
        construct may later be change.
        """
        r = self.cleaned_data['plasmid']
        if not r:
            return r
        
        assert( isinstance(r, M.DnaComponent) )
        if not r.componentType.category().id == T.dcPlasmid.id:  ## for some reason "is" doesn't work
            raise ValidationError('Given construct is not a plasmid.')
        return r
    
            
    def clean_markers(self):
        r = self.cleaned_data['markers']
        if not r.count():
            return r
        
        for m in r:
            assert( isinstance(m, M.DnaComponent))
            if not m.componentType.category().id == T.dcMarker.id:
                raise ValidationError('%s is not a marker.' % m.__unicode__() )
        return r


    class Meta:
        model = M.CellComponent
        widgets = {  ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            'description' : forms.Textarea(attrs={'cols': 100, 'rows': 10,
                                              'style':'font-family:monospace'}),
            'plasmid': sforms.AutoComboboxSelectWidget(lookup_class=L.PlasmidLookup, 
                                                       allow_new=False,
                                                       attrs={'size':35}),
            'markers' : L.FixedSelectMultipleWidget(lookup_class=L.MarkerLookup)
        }


class OligoComponentForm(forms.ModelForm, CleaningMixIn):
    """Custom form for OligoComponent Add / Change"""
    
    def __init__(self, *args, **kwargs):
        super(OligoComponentForm, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)
        
        self.fields['componentType'].initial = T.ocStandard
    
    class Meta:
        model = M.OligoComponent
        widgets = {  ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            'sequence' : forms.TextInput(attrs={'size':88}),
            'meltingTemp' : forms.TextInput(attrs={'size':4}),
            'templates' : L.FixedSelectMultipleWidget(lookup_class=L.DnaLookup),
            
            'description' : forms.Textarea(attrs={'cols': 100, 'rows': 5,
                                              'style':'font-family:monospace'}),
        }
    

class ChemicalComponentForm(forms.ModelForm, CleaningMixIn):
    """Customized Form for ChemicalComponent add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            widget=L.SilentSelectWidget,
                            queryset=M.ChemicalType.objects.filter(subTypeOf=None),
                            required=True, 
                            empty_label=None,
                            initial=T.chemOther)
    

    def __init__(self, *args, **kwargs):
        super(ChemicalComponentForm, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)

        self.fields['status'].initial = 'available'

        o = kwargs.get('instance', None)
        if o:
            self.fields['componentCategory'].initial = o.componentType.subTypeOf
        

    class Meta:
        model = M.ChemicalComponent
        widgets = {  ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            'description' : forms.Textarea(attrs={'cols': 100, 'rows': 10,
                                              'style':'font-family:monospace'}),
        }





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
    
