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
import itertools

from Bio import SeqIO

import django.forms as forms
import django.db.models as models
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
import django.contrib.messages as messages

import rotmic.models as M

import rotmic.initialTypes as T
import rotmic.initialUnits as U
import rotmic.initialComponents as IC

import rotmic.utils.sequtils as sequtils
from rotmic.utils.filefields import DocumentFormField
import rotmic.utils.ids as ids

## third-party ForeignKey lookup field
from selectable.base import ModelLookup
from selectable.registry import registry
import selectable.forms as sforms

class SilentSelectWidget( forms.Select ):
    """
    Custom Select Widget which is never reporting to have changed.
    This fixes the issue that reversion is reporting componentCategory as
    changed whenever the form is saved.
    The category field is not backed by any model value but only reports the 
    parent of componentType. That's why it cannot change by itself.
    """    
    def _has_changed(self,initial, data):
        """never mark as changed."""
        return False

class FixedSelectMultipleWidget( sforms.AutoComboboxSelectMultipleWidget ):
    """
    Bug fix the change detection method
    """    
    def _has_changed(self,initial, data):
        """override buggy method from SelectWidget"""
        old_values = [ unicode(i) for i in (initial or [u''])]
        new_values = [ unicode(i) for i in (data or [u''])]
        return not set(new_values) == set(old_values)


class DnaLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register(DnaLookup)

class OligoLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.OligoComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register(OligoLookup)

class ChemicalLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.ChemicalComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register(ChemicalLookup)


class InsertLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    filters = {'componentType__subTypeOf': T.dcFragment,
               'componentType__isInsert' : True}
    
    def get_item_id(self,item):
        return item.pk

registry.register(InsertLookup)


class VectorLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    filters = {'componentType__subTypeOf': T.dcVectorBB }
    
    def get_query(self, request, term):
        """
        Special case: sort 'unknown vector' to top.
        See: http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
        """
        q = super(VectorLookup, self).get_query(request, term)

        rest = q.exclude(id=IC.vectorUnknown.id)
        unknown = q.filter(id=IC.vectorUnknown.id)
        
        r = list(itertools.chain(unknown, rest))
        return r    
    
    def get_item_id(self,item):
        return item.pk

registry.register(VectorLookup)


class PlasmidLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    filters = {'componentType__subTypeOf': T.dcPlasmid }
    
    def get_item_id(self,item):
        return item.pk

registry.register(PlasmidLookup)


class MarkerLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    filters = {'componentType__subTypeOf': T.dcMarker }
    
    def get_item_id(self,item):
        return item.pk

registry.register(MarkerLookup)

class SampleDnaLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    filters = {'componentType__subTypeOf__in': [T.dcPlasmid, T.dcFragment] }
    
    def get_item_id(self,item):
        return item.pk

registry.register(SampleDnaLookup)

class SampleCellLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.CellComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    ##filters = {'componentType__subTypeOf__in': [T.dcPlasmid, T.dcFragment] }
    
    def get_item_id(self,item):
        return item.pk

registry.register(SampleCellLookup)


class SampleContainerLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.Container
    search_fields = ('rack__displayId__startswith',
                     'displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register(SampleContainerLookup)


class ContainerRackLookup(ModelLookup):
    """for selectable auto-completion field in Container form"""
    model = M.Rack
    search_fields = ('displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register( ContainerRackLookup )


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
                            widget=SilentSelectWidget,
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

            'insert' : sforms.AutoComboboxSelectWidget(lookup_class=InsertLookup, 
                                                       allow_new=False,
                                                       attrs={'size':35}),
            'vectorBackbone' : sforms.AutoComboboxSelectWidget(lookup_class=VectorLookup, allow_new=False),

            'markers' : FixedSelectMultipleWidget(lookup_class=MarkerLookup)
        }


class CellComponentForm(forms.ModelForm, CleaningMixIn):
    """Customized Form for DnaComponent (DNA construct) add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Species',
                            widget=SilentSelectWidget,
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
            'plasmid': sforms.AutoComboboxSelectWidget(lookup_class=PlasmidLookup, 
                                                       allow_new=False,
                                                       attrs={'size':35}),
            'markers' : FixedSelectMultipleWidget(lookup_class=MarkerLookup)
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
            'templates' : FixedSelectMultipleWidget(lookup_class=DnaLookup),
            
            'description' : forms.Textarea(attrs={'cols': 100, 'rows': 5,
                                              'style':'font-family:monospace'}),
        }
    

class ChemicalComponentForm(forms.ModelForm, CleaningMixIn):
    """Customized Form for ChemicalComponent add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            widget=SilentSelectWidget,
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


class UnitLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.Unit
    search_fields = ('name__startswith', )
    
    def get_query(self, request, term):
        """Special case: replace 'u' by \micro during autocomplete"""
        r = super(UnitLookup, self).get_query(request, term)
        
        if 'u' in term:
            microterm = term.replace('u',u"\u00B5")
            r = r | super(UnitLookup, self).get_query(request, microterm)
        return r    

    def get_item_id(self,item):
        return item.pk


class ConcentrationUnitLookup(UnitLookup):
    """Limit choices to concentration units"""
    def get_query(self, request, term):
        r = super(ConcentrationUnitLookup, self).get_query(request, term)
        return r.filter(unitType='concentration')
    
registry.register(ConcentrationUnitLookup)

class AmountUnitLookup(UnitLookup):
    """Limit choices to amount units"""
    def get_query(self, request, term):
        r = super(AmountUnitLookup, self).get_query(request, term)
        r = r.filter(unitType__in=['volume', 'mass','number'])
        return r

registry.register(AmountUnitLookup)

class VolumeAmountUnitLookup(UnitLookup):
    """Limit choices to Volume units"""
    def get_query(self, request, term):
        r = super(VolumeAmountUnitLookup, self).get_query(request, term)
        r = r.filter(unitType='volume')
        return r

registry.register(VolumeAmountUnitLookup)

def getSampleWidgets( extra={} ):
    """widgets shared between different types of Sample forms."""
    r = {
        'container' : sforms.AutoComboboxSelectWidget(lookup_class=SampleContainerLookup,
                                                     allow_new=False),

        'displayId' : forms.TextInput(attrs={'size':5}),
        
        'concentration' : forms.TextInput(attrs={'size':5}),

        'amount' : forms.TextInput(attrs={'size':5}),

        'aliquotNr' : forms.TextInput(attrs={'size':2}),
        'description': forms.Textarea(attrs={'cols': 100, 'rows': 5,
                                         'style':'font-family:monospace'}) }
    r.update( extra )
    return r

class SampleForm(forms.ModelForm):
    """Customized Form for Sample add / change. 
    To be overridden rather than used directly."""
    
    def __init__(self, *args, **kwargs):
        """Rescue request object from kwargs pushed in from SampleAdmin"""
        self.request = kwargs.pop('request', None)
        super(SampleForm, self).__init__(*args, **kwargs)

    def clean_displayId(self):
        r = self.cleaned_data['displayId']
        r = r.strip()
        
        letter, number = ids.splitSampleId( r )
        
        if number is None:
            raise ValidationError('Valid IDs must be of form "A01" or "01"')
        
        letter = letter.upper()
        number = '%02i' % number
        return letter + number
    
    
    def clean(self):
        """
        Verify that units are given if concentration and/or amount is given.
        """
        data = super(SampleForm, self).clean()
        conc = data.get('concentration', None)
        concUnit = data.get('concentrationUnit', None)
        amount = data.get('amount', None)
        amountUnit = data.get('amountUnit', None)
    
        ## reset units to None if no concentration and / or amount is given
        if not conc and concUnit:
            data['concentrationUnit'] = None
        if not amount and amountUnit:
            data['amountUnit'] = None
        
        ## validate that units are given if conc. and / or amount is given
        if conc and not concUnit:
            msg = u'please specify concentration unit'
            self._errors['concentrationUnit'] = self.error_class([msg])
    
        if amount and not amountUnit:
            msg = u'please specify amount unit'
            self._errors['amountUnit'] = self.error_class([msg])
        
        return data

    class Meta:
        model = M.Sample
        widgets = getSampleWidgets()
            


class DnaSampleForm( SampleForm ):
    """Customized Form for DnaSample add / change"""
    
    ## modify initial (default) value
    concentrationUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=ConcentrationUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=ConcentrationUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.ngul)
    
    ## restrict available choices to volume units only
    amountUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=VolumeAmountUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=VolumeAmountUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.ul)

    class Meta:
        model = M.DnaSample
        widgets = getSampleWidgets( \
            {'dna': sforms.AutoComboboxSelectWidget(lookup_class=SampleDnaLookup,
                                                    allow_new=False,
                                                    attrs={'size':35}),
             })


class CellSampleForm( SampleForm ):
    """Customized Form for CellSample add / change"""
    
    cellCategory = forms.ModelChoiceField(label='In Species',
                            widget=SilentSelectWidget,
                            queryset=M.CellComponentType.objects.filter(subTypeOf=None),
                            required=False, 
                            empty_label=None,
                            initial=T.ccEcoli)
    
    cellType = forms.ModelChoiceField(label='Strain',
                            widget=SilentSelectWidget,
                            queryset=M.CellComponentType.objects.exclude(subTypeOf=None),
                            required=False,
                            empty_label=None,
                            initial=T.ccMach1)
    
    plasmid = sforms.AutoCompleteSelectField(label='Plasmid',
                            lookup_class=PlasmidLookup,
                            required=False,
                            help_text='Start typing name or ID...',
                            widget=sforms.AutoCompleteSelectWidget(lookup_class=PlasmidLookup,
                                                        allow_new=False,
                                                        attrs={'size':35}),)

    
    ## restrict available choices to volume units only
    amountUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=VolumeAmountUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=VolumeAmountUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.ul)

    def __init__(self, *args, **kwargs):
        super(CellSampleForm, self).__init__(*args, **kwargs)

        ## keep constraint on DB level but allow user to specify via plasmid+type
        self.fields['cell'].required = False

        o = kwargs.get('instance', None)
        if o:
            self.fields['cellCategory'].initial = o.cell.componentType.category()
            self.fields['cellType'].initial = o.cell.componentType
            self.fields['plasmid'].initial = o.cell.plasmid

    def clean(self):
        """
        Verify that cell or plasmid + strain are given, create new cell if needed.
        """
        super(CellSampleForm, self).clean()
        data = self.cleaned_data
        cell = data.get('cell', None)
        plasmid = data.get('plasmid', None)
        ctype = data.get('cellType', None)
        
        if not cell and not (plasmid and ctype):
            msg = u'Please specify either an existing cell or a plasmid and strain.'
            self._errors['cell'] = self.error_class([msg])
            try: 
                del data['cell'] ## needed to really stop form saving
            except: 
                pass
            
        elif plasmid and cell:
            if plasmid != cell.plasmid:
                msg = u'Given plasmid does not match selected cell record. Remove one or the other.'
                self._errors['plasmid'] = self.error_class([msg])
                del data['plasmid']
            if ctype != cell.componentType:
                msg = u'Given strain does not match selected cell record. Clear either plasmid or cell selection.'
                self._errors['cellType'] = self.error_class([msg])
                del data['cellType']
            
        if (not cell) and plasmid:
            
            existing = M.CellComponent.objects.filter(plasmid=plasmid,
                                                    componentType=ctype)
            if existing.count():
                data['cell'] = existing.all()[0]
                messages.success(self.request, 
                                 'Attached existing cell record %s (%s) to sample.'\
                                 % (data['cell'].displayId, data['cell'].name))
            
            else:
                newcell = M.CellComponent(componentType=ctype,
                                        plasmid=plasmid,
                                        displayId=ids.suggestCellId(self.request.user.id),
                                        registeredBy = self.request.user,
                                        registeredAt = datetime.datetime.now(),
                                        name = plasmid.name + '@' + ctype.name,
                                        )
                newcell.save()
                data['cell'] = newcell
                messages.success(self.request,
                                 'Created new cell record %s (%s)' %\
                                 (newcell.displayId, newcell.name))

        return data
    
    
    class Meta:
        model = M.CellSample
        widgets = getSampleWidgets( \
            {'cell': sforms.AutoComboboxSelectWidget(lookup_class=SampleCellLookup,
                                                    allow_new=False,
                                                    attrs={'size':35}),
             })

        
class OligoSampleForm( SampleForm ):
    """Customized Form for DnaSample add / change"""
    
    ## modify initial (default) value
    concentrationUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=ConcentrationUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=ConcentrationUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.uM)
    
    ## restrict available choices to volume units only
    amountUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=VolumeAmountUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=VolumeAmountUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.ul)

    class Meta:
        model = M.OligoSample
        widgets = getSampleWidgets( \
            {'oligo': sforms.AutoComboboxSelectWidget(lookup_class=OligoLookup,
                                                      allow_new=False,
                                                      attrs={'size':35}),
             })

class ChemicalSampleForm( SampleForm ):
    """Customized Form for ChemicalSample add / change"""
    
    ## modify initial (default) value
    concentrationUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=ConcentrationUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=ConcentrationUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.M)
    
    ## restrict available choices to volume units only
    amountUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=VolumeAmountUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=AmountUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.g)

    class Meta:
        model = M.ChemicalSample
        widgets = getSampleWidgets( \
            {'chemical': sforms.AutoComboboxSelectWidget(lookup_class=ChemicalLookup,
                                                      allow_new=False,
                                                      attrs={'size':35}),
             })



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
    
    
class LocationForm(forms.ModelForm):
    """Customized Form for Location add / change"""
    
    class Meta:
        model = M.Location
        widgets = { ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            'temperature' : forms.TextInput(attrs={'size':3}),
            'room' : forms.TextInput(attrs={'size':10}),
            }


class RackForm(forms.ModelForm):
    """Customized Form for Location add / change"""
    
    class Meta:
        model = M.Rack
        widgets = { ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            }


class ContainerForm(forms.ModelForm, CleaningMixIn):
    """Customized Form for Location add / change"""
    
    ex_id = re.compile('[a-zA-Z_\-0-9\.]{3,}')
    msg_id = 'ID must be >= 3 characters and only contain: a..z, 0..9, ., _, -'
    
    class Meta:
        model = M.Container
        widgets = { ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'rack' : sforms.AutoComboboxSelectWidget(
                lookup_class=ContainerRackLookup, allow_new=False),
            'name' : forms.TextInput(attrs={'size':20}),
            }
    