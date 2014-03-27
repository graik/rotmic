## Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013 - 2014 Raik Gruenberg

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
"""Base Admin extensions used by many ModelAdmins"""

import datetime, csv, collections
from django.http import HttpResponse
from django.contrib.admin import ModelAdmin

class UserRecordMixin:
    """
    Automatically save and assign house-keeping information like by whom and
    when a record was saved.
    Create self.request variable in form.
    """

    def save_model(self, request, obj, form, change):
        """Override to save user who created this record"""
        ## do if new object or if object is being recovered by reversion
        if not change or '/recover/' in request.META['HTTP_REFERER']:
            obj.registeredBy = request.user
            obj.registeredAt = datetime.datetime.now()
            
        if change and form.has_changed():
            obj.modifiedBy = request.user
            obj.modifiedAt = datetime.datetime.now()

        obj.save()

    save_as = True  ## enable "Save as" button in all derrived classes.

class RequestFormMixin:
    """
    ModelAdmin mixin that adds a 'request' field to the form generated
    by the Admin. 

    Note: ModelFormWithRequest.__init__ is *not* called in many cases.
    
    If the Admin is using a customized form, and if this custom form class
    is overriding __init__, then this custom constructor must ensure that the 
    request parameter is removed before the classic constructor is called.
    """

    def get_form(self, request, obj=None, **kwargs):
        """
        Push request into the ModelForm. Requires the form to override __init__
        and remove request from the kwargs.
        See: http://stackoverflow.com/questions/1057252/how-do-i-access-the-request-object-or-any-other-variable-in-a-forms-clean-met
        """
        ModelForm = ModelAdmin.get_form(self, request, obj, **kwargs)

        class ModelFormWithRequest(ModelForm):
            def __init__(self, *args, **kwargs):
                """Remove request object from kwargs pushed in from Admin"""
                self.request = kwargs.pop('request', None)
                super(ModelFormWithRequest, self).__init__(*args, **kwargs)

        class ModelFormWithRequestWrapper(ModelFormWithRequest):
            """class wrapping actual model form class to capture request"""
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return ModelFormWithRequest(*args, **kwargs)

        return ModelFormWithRequestWrapper


def export_csv(request, queryset, fields):
    """
    Helper method for Admin make_csv action. Exports selected objects as 
    CSV file.
    fields - OrderedDict of name / field pairs, see Item.make_csv for example
    """
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=rotmic.csv'
    
    writer = csv.writer(response)
    writer.writerow(fields.keys())

    for o in queryset:
        columns = []
        for name,value in fields.items():
            try:
                value = eval("o.%s"%value)
                
                if type(value) not in [str, unicode] \
                   and isinstance(value, collections.Iterable):
                    value = ', '.join( [str(v) for v in value ] )
                
                columns.append( value )
            except:
                columns.append("")  ## capture 'None' fields

        columns = [ c.encode('utf-8') if type(c) is unicode else c \
                    for c in columns]
            
        writer.writerow( columns )

    return response
    
