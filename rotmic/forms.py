import os

import django.forms as forms
import django.db.models as models
from django.db.models.query import QuerySet as Q
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from rotmic.models import DnaComponent, DnaComponentType, \
     CellComponent, CellComponentType
import rotmic.initialTypes as T
import rotmic.utils.sequtils as sequtils

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


class DnaComponentForm(forms.ModelForm):
    """Customized Form for DnaComponent (DNA construct) add / change"""
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            widget=SilentSelectWidget,
                            queryset=DnaComponentType.objects.filter(subTypeOf=None),
                            required=True, 
                            empty_label=None,
                            initial=DnaComponentType.objects.get(name='Plasmid').id)
    

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
            data['marker'] = Q()
            
        ## validate that a vector backbone is given if category == Plasmid
        if category == T.dcPlasmid and not data.get('vectorBackbone',None):
            msg = u'Vector Backbone is required for Plasmids.'
            self._errors['vectorBackbone'] = self.error_class([msg])
        
        return data
      
                
    class Meta:
        model = DnaComponent
        widgets = {  ## customize widget dimensions and include dynamic select widgets
            'sequence': forms.Textarea(attrs={'cols': 100, 'rows': 4,
                                               'style':'font-family:monospace'}), 
            'comment' : forms.Textarea(attrs={'cols': 100, 'rows': 15,
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
                            initial=CellComponentType.objects.get(name='E. coli').id)
    

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
            'comment' : forms.Textarea(attrs={'cols': 100, 'rows': 15,
                                              'style':'font-family:monospace'}),
            'plasmid': sforms.AutoComboboxSelectWidget(lookup_class=PlasmidLookup, 
                                                       allow_new=False),
            'marker' : sforms.AutoComboboxSelectMultipleWidget(lookup_class=MarkerLookup)
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