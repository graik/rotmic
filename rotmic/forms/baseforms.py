import django.forms as forms

class ModelFormWithRequest(forms.ModelForm):
    """
    Modify ModelForm class to accept a request parameter in the constructor.
    Use in conjunction with RequestFormMixin / ModelAdmin.
    """
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        return super(ModelFormWithRequest,self).__init__(*args, **kwargs)
    