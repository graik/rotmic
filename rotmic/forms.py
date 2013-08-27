import django.forms as forms
from django.db.models.query import QuerySet as Q

from django_select2 import ModelSelect2Field

from rotmic.models import DnaComponent, DnaComponentType
import rotmic.initialTypes as T


class DnaComponentForm(forms.ModelForm):
    
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            queryset=DnaComponentType.objects.filter(subTypeOf=None),
                            required=True, 
                            empty_label=None,
                            initial=DnaComponentType.objects.get(name='Plasmid').id)
    
    insert2 = ModelSelect2Field(queryset=DnaComponent.objects.filter(componentType__isInsert=True))


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
