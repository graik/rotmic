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

import django.http as http

from django.contrib.admin import ModelAdmin
from django.contrib import admin
import django.contrib.admin.actions as actions
import django.core.exceptions as core

import django.contrib.messages as messages
import django.contrib.auth.models as authmodels
import django.db.models as models

from django.contrib.admin.util import NestedObjects
from django.db import DEFAULT_DB_ALIAS
from django.template.response import TemplateResponse
import django.utils.html as html
import django.utils.text as text
from django.views.decorators.csrf import csrf_protect


class UserRecordMixin:
    """
    * Automatically save and assign house-keeping information like by whom and
      when a record was saved.
    
    * Create self.request variable in form.
    
    * Block deletion of objects via delete_selected action if any of the selected
      or any related object are not listing the user as an author.
    """

    permit_delete = ['registeredBy',]
    
    actions = ['delete_selected']

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
        """
        @return True, if user is listed in any of the given fields or 
        if user is superuser
        """
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

    def related_not_authorized(self, user, objs):
        """
        Find all objects related to ``objs`` that should also be deleted. ``objs``
        must be a homogenous iterable of objects (e.g. a QuerySet).
        """
        collector = NestedObjects(using=DEFAULT_DB_ALIAS)
        collector.collect(objs)

        blocked = []
        
        for model, obj in collector.instances_with_model():
            admin_instance = admin.site._registry.get(obj.__class__, None)

            if admin_instance and hasattr(admin_instance, 'is_authorized'):
                if not admin_instance.is_authorized(user, obj):
                    blocked += [obj]

        return blocked
    
##    @csrf_protect_m
##    @transaction.atomic
    def delete_view(self, request, object_id, extra_context=None):
        "The 'delete' admin view for this model."
        blocked = []
        blocked_related = []
        obj = self.model.objects.get(id=object_id)
        
        if not self.is_authorized(request.user, obj):
            blocked = [ obj ]
        
        if not blocked:
            blocked_related = self.related_not_authorized(request.user, [obj])
            
            if not blocked_related:
                ## let default Admin delete_view handle all other cases
                return ModelAdmin.delete_view(self, request, object_id, 
                                              extra_context=extra_context)
            
        return self.delete_blocked_response(request, [obj], blocked, blocked_related,
                                            template='delete_blocked.html')


    def delete_selected(self, request, queryset):
        """
        Override the built-in admin.site.delete_selected action to check
        each object against the is_authorized method.

        Note: this admin-specific action is only used if 'delete_selected'
        is explicitely included in actions=[...]. Otherwise, the site-wide
        default method is used.
        """
        blocked = []
        blocked_related = []
        
        for obj in queryset:
            if not self.is_authorized(request.user, obj):
                blocked += [ obj ]        
        
        if not blocked:
            
            blocked_related = self.related_not_authorized(request.user, queryset)
            
            if not blocked_related:
                ## Call default admin delete_selected action
                return actions.delete_selected(self, request, queryset)
    
        return self.delete_blocked_response(request, queryset, blocked, blocked_related)
        
    delete_selected.short_description = "Delete selected %(verbose_name_plural)s"


    def delete_blocked_response(self, request, deleteset, 
                                blocked=[], blocked_related=[],
                                template='delete_selected_blocked.html'):        
        """
        @param deleteset: queryset or [], the objects for which deletion is requested
        @param blocked: queryset or [], those from deleteset for which user has no delete permission
        @param blocked_related: queryset or [], related objects for which permission is missing

        @return TemplateResponse, a response object for the view that shows up if the user is 
        blocked from deleting one or several objects.
        """
        ## the following code is a simplification of the original delete_selected display code
        opts = self.model._meta
        app_label = opts.app_label
        objects_name = opts.verbose_name
        if len(deleteset) > 1:
            objects_name += 's'
        title = "Cannot delete %(name)s" % {"name": objects_name}
        
        def format_obj(obj):
            return html.format_html('{0}: <a href="{1}">{2}</a>',
                               text.capfirst(obj._meta.verbose_name),
                               obj.get_absolute_url(),
                               obj)

        blocked = [format_obj(o) for o in blocked]
        blocked_related = [format_obj(o) for o in blocked_related]

        context = {
            "title": title,
            "objects_name": objects_name,
            "object": deleteset[0],
            "deletable_objects": [],
            'queryset': deleteset,
            "blocked_related": blocked_related,
            "blocked": blocked,
            "opts": opts,
            "app_label": app_label,
            'preserved_filters': [],           
            'action_checkbox_name': 'delete_selected',
        }

        return TemplateResponse(request, [
            "admin/%s/%s/%s" % (app_label, opts.model_name, template),
            "admin/%s/%s.html" % (app_label, template),
            "admin/%s" % template,
            ], context, current_app=self.admin_site.name)
        

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


class UpdateManyMixin:
    """ModelAdmin mixin adding an action method for the multi-object update dialog"""

    def make_update(self, request, queryset):
        """List view action for bulk update dialog"""
        ## see https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#actions-that-provide-intermediate-pages

        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        modelname = self.model._meta.object_name.lower()
        return http.HttpResponseRedirect("/rotmic/update/%s/?entries=%s" \
                                    % (modelname, ",".join(selected)))

    make_update.short_description = 'Edit all selected records at once'

    

def export_csv(request, queryset, fields):
    """
    Helper method for Admin make_csv action. Exports selected objects as 
    CSV file.
    fields - OrderedDict of name / field pairs, see Item.make_csv for example
    """
    response = http.HttpResponse(mimetype='text/csv')
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
    
