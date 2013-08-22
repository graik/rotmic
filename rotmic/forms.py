import django.forms as forms
from django.db.models.query import QuerySet as Q

from rotmic.models import DnaComponent, DnaComponentType


class DnaComponentForm(forms.ModelForm):
    
    typePlasmid = DnaComponentType.objects.get(name='Plasmid')
    typeInsert = DnaComponentType.objects.get(name='Insert')
    typeVectorBB = DnaComponentType.objects.get(name='Vector Backbone')
    typeMarker = DnaComponentType.objects.get(name='Marker')
    
    componentCategory = forms.ModelChoiceField(label='Category',
                            queryset=DnaComponentType.objects.filter(subTypeOf=None),
                            required=True, 
                            empty_label=None,
                            initial=DnaComponentType.objects.get(name='Plasmid').id)

    componentType = forms.ModelChoiceField(label='Type',
                            queryset=DnaComponentType.objects.exclude(subTypeOf=None),
                            required=True,
                            initial=DnaComponentType.objects.get(name='generic plasmid').id,
                            empty_label=None)
    
    insert = forms.ModelChoiceField(label='Insert',
                            queryset=DnaComponent.objects.filter(componentType__subTypeOf=typeInsert),
                            required=False,
                            empty_label='no insert')
        
    vectorBackbone = forms.ModelChoiceField(label='Vector Backbone',
                            queryset=DnaComponent.objects.filter(componentType__subTypeOf=typeVectorBB),
                            required=False,
                            empty_label='---specify backbone---')

    marker = forms.ModelMultipleChoiceField(label='Marker',
                            queryset=DnaComponent.objects.filter(componentType__subTypeOf=typeMarker),
                            required=False)


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

        if category != self.typePlasmid:
            data['insert'] = None
            data['vectorBackbone'] = None
            data['circular'] = False
        
        if category not in [self.typeVectorBB, self.typeInsert] and 'marker' in data:
            data['marker'] = Q()
        
        return data
      
                
    class Meta:
        model = DnaComponent
        widgets = {  ## customize widget dimensions
            'sequence' : forms.Textarea(attrs={'cols': 80, 'rows': 4}) 
        }
