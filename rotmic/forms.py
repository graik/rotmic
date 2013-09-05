import django.forms as forms
from django.db.models.query import QuerySet as Q

from rotmic.models import DnaComponent, DnaComponentType
import rotmic.initialTypes as T

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


class DnaComponentForm(forms.ModelForm):
    
    
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
