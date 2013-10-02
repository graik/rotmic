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
import os

import django.forms as forms
import django.db.models as models
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from rotmic.models import DnaComponent, DnaComponentType, \
     CellComponent, CellComponentType, Sample, DnaSample,\
     Location, Rack, Container, Unit

import rotmic.initialTypes as T
import rotmic.initialUnits as U
import rotmic.utils.sequtils as sequtils
from rotmic.utils.filefields import DocumentFormField

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


class InsertLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    filters = {'componentType__subTypeOf': T.dcFragment,
               'componentType__isInsert' : True}
    
    def get_item_id(self,item):
        return item.pk

registry.register(InsertLookup)


class VectorLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    filters = {'componentType__subTypeOf': T.dcVectorBB }
    
    def get_item_id(self,item):
        return item.pk

registry.register(VectorLookup)


class PlasmidLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    filters = {'componentType__subTypeOf': T.dcPlasmid }
    
    def get_item_id(self,item):
        return item.pk

registry.register(PlasmidLookup)


class MarkerLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    filters = {'componentType__subTypeOf': T.dcMarker }
    
    def get_item_id(self,item):
        return item.pk

registry.register(MarkerLookup)

class SampleDnaLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    filters = {'componentType__subTypeOf__in': [T.dcPlasmid, T.dcFragment] }
    
    def get_item_id(self,item):
        return item.pk

registry.register(SampleDnaLookup)


class SampleContainerLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = Container
    search_fields = ('rack__displayId__startswith',
                     'displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register(SampleContainerLookup)


class ContainerRackLookup(ModelLookup):
    """for selectable auto-completion field in Container form"""
    model = Rack
    search_fields = ('displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register( ContainerRackLookup )


class DnaComponentForm(forms.ModelForm):
    """Customized Form for DnaComponent (DNA construct) add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            widget=SilentSelectWidget,
                            queryset=DnaComponentType.objects.filter(subTypeOf=None),
                            required=True, 
                            empty_label=None,
                            initial=T.dcPlasmid)
    
    ## genbankFile upload into textfield 'genbank' is handled by ModelAdmin.save_model
    genbankFile = DocumentFormField(label='GenBank file', required=False,
                                    help_text='upload genbank-formatted file',
                                     extensions=['gbk','gb','genebank'])
    

    def __init__(self, *args, **kwargs):
        super(DnaComponentForm, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)

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
    

    def clean(self):
        """
        Remove values for hidden fields, which might have been set before final
        category was selected.
        Note: this is also partly enforced by the DnaComponent.save method.
        """
        data = super(DnaComponentForm, self).clean()
        category = data['componentCategory'] 

        if category != T.dcPlasmid:
            data['insert'] = None
            data['vectorBackbone'] = None
        
        if category not in [T.dcVectorBB, T.dcFragment] and 'marker' in data:
            data['marker'] = QuerySet()
            
        ## validate that a vector backbone is given if category == Plasmid
        if category == T.dcPlasmid and not data.get('vectorBackbone',None):
            msg = u'Vector Backbone is required for Plasmids.'
            self._errors['vectorBackbone'] = self.error_class([msg])
        
        return data
      
                
    class Meta:
        model = DnaComponent
        widgets = {  ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            'sequence': forms.Textarea(attrs={'cols': 100, 'rows': 4,
                                               'style':'font-family:monospace'}), 
            'comment' : forms.Textarea(attrs={'cols': 100, 'rows': 10,
                                              'style':'font-family:monospace'}),
            'insert' : sforms.AutoComboboxSelectWidget(lookup_class=InsertLookup, allow_new=False),
            'vectorBackbone' : sforms.AutoComboboxSelectWidget(lookup_class=VectorLookup, allow_new=False)
        }


class CellComponentForm(forms.ModelForm):
    """Customized Form for DnaComponent (DNA construct) add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            widget=SilentSelectWidget,
                            queryset=CellComponentType.objects.filter(subTypeOf=None),
                            required=True, 
                            empty_label=None,
                            initial=T.ccEcoli)
    

    def __init__(self, *args, **kwargs):
        super(CellComponentForm, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)

        o = kwargs.get('instance', None)
        if o:
            self.fields['componentCategory'].initial = o.componentType.subTypeOf
        


    def clean(self):
        """
        Remove values for hidden fields, which might have been set before final
        category was selected.
        Note: this is also partly enforced by the DnaComponent.save method.
        """
        data = super(CellComponentForm, self).clean()
        category = data['componentCategory'] 

        return data
      
                
    class Meta:
        model = CellComponent
        widgets = {  ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            'comment' : forms.Textarea(attrs={'cols': 100, 'rows': 10,
                                              'style':'font-family:monospace'}),
            'plasmid': sforms.AutoComboboxSelectWidget(lookup_class=PlasmidLookup, 
                                                       allow_new=False),
            'marker' : FixedSelectMultipleWidget(lookup_class=MarkerLookup)
        }


class UnitLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = Unit
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
##        'concentrationUnit':sforms.AutoComboboxSelectWidget(lookup_class=ConcentrationUnitLookup,
##                                allow_new=False,
##                                attrs={'size':5}),        

        'amount' : forms.TextInput(attrs={'size':5}),
##        'amountUnit':sforms.AutoComboboxSelectWidget(lookup_class=AmountUnitLookup,
##                                allow_new=False,
##                                attrs={'size':5}),        

        'aliquotNr' : forms.TextInput(attrs={'size':2}),
        'comment': forms.Textarea(attrs={'cols': 100, 'rows': 5,
                                         'style':'font-family:monospace'}) }
    r.update( extra )
    return r

class SampleForm(forms.ModelForm):
    """Customized Form for Sample add / change"""
    
    ## defining a form field seems to be the only way for providing an intial value
    concentrationUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=ConcentrationUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=ConcentrationUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.uM)

    ## defining a form field seems to be the only way for providing an intial value
    amountUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=AmountUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=AmountUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.ul)

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
            del data['concentrationUnit']
        if not amount and amountUnit:
            del data['amountUnit']
        
        ## validate that units are given if conc. and / or amount is given
        if conc and not concUnit:
            msg = u'please specify concentration unit'
            self._errors['concentrationUnit'] = self.error_class([msg])
    
        if amount and not amountUnit:
            msg = u'please specify amount unit'
            self._errors['amountUnit'] = self.error_class([msg])
        
        return data

    class Meta:
        model = Sample
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
        model = DnaSample
        widgets = getSampleWidgets( \
            {'dna': sforms.AutoComboboxSelectWidget(lookup_class=SampleDnaLookup,
                                                    allow_new=False),
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
        model = Location
        widgets = { ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            'temperature' : forms.TextInput(attrs={'size':3}),
            'room' : forms.TextInput(attrs={'size':10}),
            }


class RackForm(forms.ModelForm):
    """Customized Form for Location add / change"""
    
    class Meta:
        model = Rack
        widgets = { ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            }


class ContainerForm(forms.ModelForm):
    """Customized Form for Location add / change"""
    
    class Meta:
        model = Container
        widgets = { ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'rack' : sforms.AutoComboboxSelectWidget(
                lookup_class=ContainerRackLookup, allow_new=False),
            'name' : forms.TextInput(attrs={'size':20}),
            }
    