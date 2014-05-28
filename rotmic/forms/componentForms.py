
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
import re, datetime, StringIO

from Bio import SeqIO

import django.forms as forms
import django.db.models as models
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
import django.contrib.messages as messages

from .baseforms import ModelFormWithRequest

import rotmic.models as M

import rotmic.initialTypes as T
import rotmic.initialUnits as U

import rotmic.utils.sequtils as sequtils
from rotmic.utils.filefields import DocumentFormField

import selectLookups as L
import selectable.forms as sforms

    
class CleaningMixIn:
    """enforce displayID pattern"""
    
    ex_id = re.compile('[a-z]{1,6}[0-9]{4}[a-z]{0,1}')
    msg_id = 'ID must have format a[bcdef]0123[a]. Example: rg0022 or mtz9900b'  ## for human-readable messages

    def clean_displayId(self):
        """enforce letter-digit displayId: a(bcdef)0123(a)"""
        r = self.cleaned_data['displayId']
        r = r.strip()

        if not self.ex_id.match(r):
            raise ValidationError(self.msg_id)
        return r


def getComponentWidgets( extra={} ):
    """widgets shared between different types of Component forms."""
    r = {'displayId' : forms.TextInput(attrs={'size':10}),
         'name' : forms.TextInput(attrs={'size':25}),

         'description' : forms.Textarea(attrs={'cols': 100, 'rows': 10,
                                          'style':'font-family:monospace'}),
         
         'projects': L.FixedSelectMultipleWidget(lookup_class=L.ProjectLookup,),

         'authors': L.FixedSelectMultipleWidget(lookup_class=L.UserLookup,),
         }
    r.update( extra )
    return r


class ComponentForm(ModelFormWithRequest, CleaningMixIn):
        
    def __init__(self, *args, **kwargs):
        """
        relies on self.request which is created by ModelFormWithRequest
        via customized ModelAdmin
        """
        super(ComponentForm, self).__init__(*args, **kwargs)

        # general field modifications
        self.fields['projects'].widget.can_add_related = False
        self.fields['authors'].widget_can_add_related = False
        if self.request:
            self.fields['authors'].initial = [self.request.user]
        
        o = kwargs.get('instance', None)
        
        # GET or POST with existing instance
        if o and 'componentCategory' in self.fields:
            self.fields['componentCategory'].initial = o.componentType.subTypeOf
        
        # POST with data attached to previously existing instance
        ## Note: by calling has_changed here, we populate the _changed_data dict
        ## any further modifications go under the radar.
        if o and self.data and self.request and self.has_changed():        
            self.data['modifiedBy'] = self.request.user.id
            self.data['modifiedAt'] = datetime.datetime.now()
            

    def clean_authors(self):
        """Prevent non-authors from changing authorship"""
        r = self.cleaned_data['authors']
        u = self.request.user
        
        if self.instance and self.instance.id and ('authors' in self.changed_data):
            if not self.instance.authors.filter(id=u.id).exists()\
               and not u == self.instance.registeredBy\
               and not u.is_superuser:
                raise ValidationError, 'Sorry, only authors or creators can change this field.'
        
        return r
    
    @property
    def changed_data(self):
        r = super(ComponentForm,self).changed_data
        
        ## filter out any form fields that do not exist on the model
        r = [ a for a in r if getattr(self.instance, a, None) ]

        return r
    
    class Meta:
        model = M.Component
        widgets = getComponentWidgets()


class GenbankComponentForm(ComponentForm):
    """
    Extend the form with a GenBank file upload field which is used by
    both DNA and ProteinComponent. The underlying model is assumed to have
    a field 'genbank' which will receive a text copy of the genbank content
    and a field 'sequence' which will receive the DNA / Protein sequence.
    """

    genbankFile = DocumentFormField(label='GenBank file', required=False,
                                    help_text='This will replace the current raw sequence.',
                                     extensions=['gbk','gb','genebank'])
    
    genbankClear = forms.BooleanField(label='Clear attached genBank record', 
                        required=False,
                        help_text='Note: this will not remove the raw sequence.',
                        initial=False)

    def __init__(self, *args, **kwargs):
        super(GenbankComponentForm, self).__init__(*args, **kwargs)
        
        self.fields['sequence'].label = 'Raw Sequence'
        
        if self.instance:
            if not self.instance.genbank:
                self.fields['genbankClear'].widget.attrs['readonly'] = True
                self.fields['genbankClear'].help_text = 'No genbank record currently attached'

    def extractGenbank(self, data):
        """extract genbank file from upload field"""
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
                    
                    return True
        except StopIteration:
            msg = 'Empty or corrupted genbank file'
            self._errors['genbankFile'] = self.error_class([msg])
        except ValueError, why:
            msg = 'Error reading genbank file: %r' % why
            self._errors['genbankFile'] = self.error_class([msg])

        return False
    
    def clean(self):
        """extract sequence from genbank record and copy record into textfield"""
        data = super(GenbankComponentForm, self).clean()
        
        if data.get('genbankClear',False):
            data['genbankFile'] = None
            
        self.extractGenbank(data)
        
        return data
    
    def save(self, commit=True):
        m = super(GenbankComponentForm, self).save(commit=False)

        if self.cleaned_data.get('genbankClear', False):
            m.genbank = None
        
        if commit:
            m.save()
            self.save_m2m()

        return m
     

class DnaComponentForm(GenbankComponentForm):
    """Customized Form for DnaComponent (DNA construct) add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            queryset=M.DnaComponentType.objects.filter(subTypeOf=None),
                            required=False, 
                            empty_label=None)

    def __init__(self, *args, **kwargs):
        super(DnaComponentForm, self).__init__(*args, **kwargs)

        o = kwargs.get('instance', None)

        ## Add New form
        if not o:
            self.fields['componentCategory'].initial = T.dcPlasmid
            self.fields['componentType'].initial = T.dcPlasmidGeneric

            ## pre-set category if 'translatesTo' is given as URL parameter
            ## currently this doesn't seem to work
            if 'translatesTo' in self.initial:
                self.initial['componentType'] = unicode(T.dcFragmentCDS.pk)
                self.initial['componentCategory'] = unicode(T.dcFragment.pk)
    
    def clean_sequence(self):
        """Enforce DNA sequence."""
        r = self.cleaned_data['sequence']
        if not r:
            return r

        r = sequtils.cleanseq( r )
        
        if not sequtils.isdna( r ):
            raise ValidationError('This is not a DNA sequence.', code='invalid')        
        return r
    
    def clean_componentType(self):
        r = self.cleaned_data['componentType']
        cat = r.category()
        old = M.DnaComponentType.objects.get(id=self.initial['componentType']).category()
        
        if cat.id == old.id: ## only worry if category had changed
            return r

        if self.instance and self.instance.id and ('componentType' in self.changed_data):
            assert( isinstance(cat, M.DnaComponentType) )
            msg = 'Cannot change category / type: '

            if cat.id != T.dcVectorBB and self.instance.as_vector_in_plasmid.count():
                raise ValidationError(msg + 'This construct is in use as a vector backbone.')
            
            if not cat.id in [T.dcFragment.id, T.dcMarker.id] and \
               self.instance.as_insert_in_dna.count():
                raise ValidationError(msg + 'This construct is in use as an insert.')
                
            if cat.id != T.dcMarker and (self.instance.as_marker_in_cell.count() \
                                       or self.instance.as_marker_in_dna.count() ):
                raise ValidationError(msg + 'This construct is in use as a marker.')
        
            if cat.id != T.dcPlasmid and self.instance.as_plasmid_in_cell.count():
                raise ValidationError(msg + 'This construct is in use as a plasmid.')
        return r
    
    
    def _validateLinked(self, x, categories=[T.dcFragment,T.dcMarker]):
        """
        Enforce that linked DC instances have given categories and check
        for circular references
        """
        if x:
            cat_ids = [ cat.id for cat in categories ]
            if not x.componentType.category().id in cat_ids:
                msg = 'Constructs of category %s are not allowed here.'\
                    % x.componentType.category().name
                self._errors[field] = self.error_class([msg])
        
            if x.id == self.instance.id: 
                self._errors[field] = self.error_class(['Circular reference!'])
    
    def _validateLinkedMany(self, query, categories=[]):
        """validate all instances in Many2Many relation"""
        for x in query:
            self._validateLinked(x, categories=categories)


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
            
        if category and (category != T.dcFragment):
            data['translatesTo'] = None
        
        if category and (category not in [T.dcVectorBB, T.dcFragment] and 'markers' in data):
            data['markers'] = []
            
        ## validate that a vector backbone is given if category == Plasmid
        if category == T.dcPlasmid and not data.get('vectorBackbone',None):
            msg = u'Vector Backbone is required for Plasmids.'
            self._errors['vectorBackbone'] = self.error_class([msg])
        
        ## validate Insert, Marker, Vector, and Protein categories
        self._validateLinked(data['insert'], [T.dcFragment, T.dcMarker])
        
        self._validateLinked(data['vectorBackbone'], [T.dcVectorBB])
        
        self._validateLinked(data['translatesTo'], [T.pcProtein])

        self._validateLinkedMany(data['markers'], [T.dcMarker])
        
        return data
      
                
    class Meta:
        model = M.DnaComponent

        widgets = getComponentWidgets( extra={
            'sequence': forms.Textarea(attrs={'cols': 100, 'rows': 4,
                                               'style':'font-family:monospace'}), 

            'insert' : sforms.AutoComboboxSelectWidget(lookup_class=L.InsertLookup, 
                                                       allow_new=False,
                                                       attrs={'size':32}),
            'vectorBackbone' : sforms.AutoComboboxSelectWidget(
                                                  lookup_class=L.VectorLookup, 
                                                  allow_new=False),

            'markers' : L.FixedSelectMultipleWidget(lookup_class=L.MarkerLookup),
            
            'translatesTo' : sforms.AutoComboboxSelectWidget(
                                                 lookup_class=L.ProteinLookup,
                                                 allow_new=False)
            })


class CellComponentForm(ComponentForm):
    """Customized Form for DnaComponent (DNA construct) add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Species',
                            queryset=M.CellComponentType.objects.filter(subTypeOf=None),
                            required=False, 
                            empty_label=None)
##                            initial=T.ccEcoli)
    

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
        widgets = getComponentWidgets( extra={
            'plasmid': sforms.AutoComboboxSelectWidget(lookup_class=L.PlasmidLookup, 
                                                       allow_new=False,
                                                       attrs={'size':35}),
            'markers' : L.FixedSelectMultipleWidget(lookup_class=L.MarkerLookup)
            })


class OligoComponentForm(ComponentForm):
    """Custom form for OligoComponent Add / Change"""
    
    def __init__(self, *args, **kwargs):
        super(OligoComponentForm, self).__init__(*args, **kwargs)
        
        o = kwargs.get('instance', None)
        ## "Add New" Form
        if not o:
            self.fields['componentType'].initial = T.ocStandard
    
    def clean_sequence(self):
        """Enforce DNA sequence."""
        r = self.cleaned_data['sequence']
        if not r:
            return r

        r = sequtils.cleanseq( r )
        
        if not sequtils.isdna( r ):
            raise ValidationError('This is not a DNA sequence.', code='invalid')        
        return r

    class Meta:
        model = M.OligoComponent
        widgets = getComponentWidgets( extra={
            'sequence' : forms.TextInput(attrs={'size':88}),
            'meltingTemp' : forms.TextInput(attrs={'size':4}),
            'templates' : L.FixedSelectMultipleWidget(lookup_class=L.DnaLookup),
            'reversePrimers' : L.FixedSelectMultipleWidget(lookup_class=L.OligoLookup),
            } )
    

class ChemicalComponentForm(ComponentForm):
    """Customized Form for ChemicalComponent add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            queryset=M.ChemicalType.objects.filter(subTypeOf=None),
                            required=False, 
                            empty_label=None)
##                            initial=T.chemOther)
    

    def __init__(self, *args, **kwargs):
        super(ChemicalComponentForm, self).__init__(*args, **kwargs)
        
        o = kwargs.get('instance', None)
        ## "Add New" Form
        if not o:
            self.fields['status'].initial = 'available'
        

    class Meta:
        model = M.ChemicalComponent
        widgets = getComponentWidgets( extra={} )

    
class ProteinComponentForm(GenbankComponentForm):
    """Customized Form for ProteinComponent add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            queryset=M.ProteinComponentType.objects.filter(subTypeOf=None),
                            required=False, 
                            empty_label=None)
##                            initial=T.pcProtein)
    
   
    ## hidden field which can be set through URL parameter
    encodedBy = forms.CharField(label='', 
                                widget=forms.HiddenInput,
                                required=False)
    

    def __init__(self, *args, **kwargs):
        super(ProteinComponentForm, self).__init__(*args, **kwargs)

        o = kwargs.get('instance', None)
        ## "Add New" Form
        if not o:
            self.fields['status'].initial = 'available'
            self.fields['componentType'].initial = T.pcOther
            self.fields['componentCategory'].initial = T.pcProtein
                
    def clean_sequence(self):
        """Enforce Protein sequence."""
        r = self.cleaned_data['sequence']
        if not r:
            return r

        r = sequtils.cleanseq( r )
        
        if not sequtils.isaa( r ):
            raise ValidationError('This is not a protein sequence.', code='invalid')        
        return r
    
    def clean_encodedBy(self):
        """Convert hidden field value to DC instance (from URL parameter)"""
        r = self.cleaned_data['encodedBy']
        try:
            if r:
                r = int(r)
                instance = M.DnaComponent.objects.get(id=r)
                return instance
        except M.DnaComponent.DoesNotExist:
            raise forms.ValidationError()
        return ''
    
    
    class Meta:
        model = M.ProteinComponent
        widgets = getComponentWidgets( extra={
            'sequence': forms.Textarea(attrs={'cols': 100, 'rows': 4,
                                               'style':'font-family:monospace'}), 
            })
