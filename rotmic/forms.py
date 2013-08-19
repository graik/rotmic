import django.forms as forms

from rotmic.models import DnaComponent, DnaComponentType


class DnaComponentForm(forms.ModelForm):
    componentCategory = forms.ModelChoiceField(label='Category',
                                               queryset=DnaComponentType.objects.filter(subTypeOf=None),
                                               required=True, 
                                               widget=forms.RadioSelect, empty_label=None)
    componentType = forms.ModelChoiceField(label='Type',
                                           queryset=DnaComponentType.objects.exclude(subTypeOf=None),
                                           required=True, 
                                           widget=forms.RadioSelect, empty_label=None)
##    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'rows': 4}),required=False)
    sequence = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 4}),required=False)
    
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DnaComponentForm, self).__init__(*args, **kwargs)
                
    class Meta:
        model = DnaComponent 
