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
import django.contrib.messages as messages
import django.contrib.auth.models as authmodels
import django.db.models as models

class UserRecordMixin:
    """
    * Automatically save and assign house-keeping information like by whom and
      when a record was saved.
    * Create self.request variable in form.
    """

    permit_delete = ['registeredBy',]

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
    

    def is_authorized(self, user, obj, fields=None):
        """@return True, if user is listed in any of the given fields"""
        fields = fields or self.permit_delete
        userpk = user.pk
        
        if user.is_superuser:
            return True
        
        for fieldname in fields:
            f = eval('obj.%s' % fieldname)
          
            if isinstance(f, authmodels.User):
                if f.pk == userpk:
                    return True

            elif isinstance(f, models.Manager):
                if f.filter(id=userpk).exists():
                    return True
            else:
                raise models.ImproperlyConfigured(\
                    'Cannot match %s to any field of %r' % (fieldname, obj) )
        
        return False
        

    def has_delete_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to delete the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to delete *any* object of the given type.
        """
        r = ModelAdmin.has_delete_permission(self, request, obj)
        
        if obj and r:
            r = self.is_authorized(request.user, obj)

        return r

                    

class RequestFormMixin:
    """
    ModelAdmin mixin that adds a 'request' field to the form generated
    by the Admin. 
    
    Note: The Admin class *must* use a custom form derrived from 
    rotmic.baseforms.ModelFormWithRequest which removes the unexpected
    'request' parameter from the constructor and pushes it to self.request.
    """

    def get_form(self, request, obj=None, **kwargs):
        """
        Push request into the ModelForm. Requires the form to override __init__
        and remove request from the kwargs.
        See: http://stackoverflow.com/questions/1057252/how-do-i-access-the-request-object-or-any-other-variable-in-a-forms-clean-met
        """
        ModelForm = ModelAdmin.get_form(self, request, obj, **kwargs)

        class ModelFormWithRequestWrapper(ModelForm):
            """class wrapping actual model form class to capture request"""
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return ModelForm(*args, **kwargs)

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
    
