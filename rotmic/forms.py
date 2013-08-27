import django.forms as forms
from django.db.models.query import QuerySet as Q

from rotmic.models import DnaComponent, DnaComponentType
import rotmic.initialTypes as T

## third-party ForeignKey lookup field
from selectable.base import ModelLookup
from selectable.registry import registry
import selectable.forms as sforms

class DnaComponentLookup(ModelLookup):
    model = DnaComponent
    search_fields = ('displayId__icontains', 'name__icontains')
    
    def get_item_id(self,item):
        return item.displayId

registry.register(DnaComponentLookup)

class DnaComponentForm(forms.ModelForm):
    
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            queryset=DnaComponentType.objects.filter(subTypeOf=None),
                            required=True, 
                            empty_label=None,
                            initial=DnaComponentType.objects.get(name='Plasmid').id)
    

    autoInsert = sforms.AutoCompleteSelectField(lookup_class=DnaComponentLookup, allow_new=True)

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
        
        return data
      
                
    class Meta:
        model = DnaComponent
        widgets = {  ## customize widget dimensions
            'sequence' : forms.Textarea(attrs={'cols': 80, 'rows': 4}) 
        }
