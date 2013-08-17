import django.forms as forms
from rotmic.models import DnaComponent, DnaComponentType

class DnaComponentForm(forms.ModelForm):
    componentType = forms.ModelMultipleChoiceField(label='Category',queryset=DnaComponentType.objects.filter(subTypeOf=None),required=False)
##    componentSubType = forms.ModelMultipleChoiceField(label='Type',queryset=DnaComponentType.objects.all(),required=False)
##    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'rows': 4}),required=False)
##    sequence = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'rows': 4}),required=False)
    
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DnaComponentForm, self).__init__(*args, **kwargs)
                
    class Meta:
        model = DnaComponent 
