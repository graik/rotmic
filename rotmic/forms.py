import django.forms as forms

from rotmic.models import DnaComponent, DnaComponentType


class DnaComponentForm(forms.ModelForm):
    
    componentCategory = forms.ModelChoiceField(label='Category',
                                               queryset=DnaComponentType.objects.filter(subTypeOf=None),
                                               required=True, 
                                               empty_label=None,
                                               initial=DnaComponentType.objects.get(name='Plasmid').id)

    componentType = forms.ModelChoiceField(label='Type',
                                           queryset=DnaComponentType.objects.exclude(subTypeOf=None),
                                           required=True,
                                           initial=DnaComponentType.objects.get(name='generic plasmid').id,
                                           widget=forms.RadioSelect, empty_label=None)
    
    
    def __init__(self, *args, **kwargs):
        super(DnaComponentForm, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)

        o = kwargs.get('instance', None)
        if o:
            self.fields['componentCategory'].initial = o.componentType.subTypeOf
        
                
    class Meta:
        model = DnaComponent
        widgets = {  ## customize widget dimensions
            'sequence' : forms.Textarea(attrs={'cols': 80, 'rows': 4}) 
        }
