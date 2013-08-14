from django.contrib import admin

## imports for overriding ModelAdmin
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.admin import widgets, helpers
from django.template import loader, Context, RequestContext
from django.template.response import TemplateResponse
from django.contrib.admin.util import unquote, flatten_fieldsets, get_deleted_objects, model_format_dict
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text

from functools import update_wrapper, partial
csrf_protect_m = method_decorator(csrf_protect)

## imports for overriding ChangeList
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.util import quote



class ViewFirstChangeList( ChangeList ):
    """
    Modify the admin ChangeList so that items are linked to the readonly
    view rather than to the Edit form (ChangeForm).
    """
    
    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return reverse('admin:%s_%s_readonly' % (self.opts.app_label,
                                               self.opts.module_name),
                       args=(quote(pk),),
                       current_app=self.model_admin.admin_site.name)
    

class ViewFirstModelAdmin( admin.ModelAdmin ):
    """
    Custom version of admin.ModelAdmin which shows a read-only
    View for a given object instead of the normal ChangeForm. The changeForm
    is accessed by admin/ModelName/id/edit
    """
    
    def get_urls(self):
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.changelist_view),
                name='%s_%s_changelist' % info),
            url(r'^add/$',
                wrap(self.add_view),
                name='%s_%s_add' % info),
            url(r'^(.+)/history/$',
                wrap(self.history_view),
                name='%s_%s_history' % info),
            url(r'^(.+)/delete/$',
                wrap(self.delete_view),
                name='%s_%s_delete' % info),
            url(r'^(.+)/edit/$',
                wrap(self.change_view),
                name='%s_%s_change' % info),
            url(r'^(.+)/$',
                wrap(self.readonly_view),
                name='%s_%s_readonly' % info),
        )
        return urlpatterns
    
    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page. Override
        to use our customized ChangeList.
        """
        return ViewFirstChangeList


    @csrf_protect_m
    def readonly_view(self, request, object_id, form_url='', extra_context=None):
        "The 'readonly' admin view for this model."
        model = self.model
        opts = model._meta
        app_label = opts.app_label       
        obj = self.get_object(request, unquote(object_id))

##        if not self.has_change_permission(request, obj):
##            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_text(opts.verbose_name), 'key': escape(object_id)})
        
        context = {
            'title': _('Read %s') % force_text(opts.verbose_name),
##            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'media': self.media,
##            'inline_admin_formsets': inline_admin_formsets,
##            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
        }
        context.update({
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'opts': opts,
        })        
        context.update(extra_context or {})

        return TemplateResponse(request, [
            "admin/%s/%s/readonly_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/readonly_form.html" % app_label,
            "admin/readonly_form.html"
        ], context, current_app=self.admin_site.name)

