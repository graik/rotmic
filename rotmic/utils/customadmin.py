from django.contrib import admin

## imports for overriding ModelAdmin
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.admin import widgets, helpers, ModelAdmin
from django.template import loader, Context, RequestContext
from django.template.response import TemplateResponse
from django.contrib.admin.util import unquote, flatten_fieldsets, get_deleted_objects, model_format_dict
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
import django.utils.html as html
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters

## imports for show / display links
from django.utils.safestring import mark_safe
import django.utils.html as html

from functools import update_wrapper, partial
csrf_protect_m = method_decorator(csrf_protect)

## imports for overriding ChangeList
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.util import quote

## comment handling
import ratedcomments.models as CM
import ratedcomments.templatetags.commenttags as commenttags
import django.contrib.contenttypes.models as CT
import django.contrib.staticfiles.templatetags.staticfiles as ST

import rotmic.models as M
import rotmic.templatetags.rotmicfilters as F


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
    

class ViewFirstModelAdmin( ModelAdmin ):
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
            # re-route change view to <id>/edit/
            url(r'^(.+)/edit/$',
                wrap(self.change_view),
                name='%s_%s_change' % info),
                        
            # new default view is readonly
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
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_text(opts.verbose_name), 'key': html.escape(object_id)})
        
        context = {
##            'title': _('Read %s') % force_text(opts.verbose_name),
##            'adminform': adminForm,
            'object_id': object_id,
            'o': obj,
            'is_popup': "_popup" in request.REQUEST,
            'media': self.media,
##            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
            ## provide class name for titles and bread crums
            'class_label': obj._meta.verbose_name or obj.__class__.__name__
        }
        context.update({
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'opts': opts,
        })        
        context.update(extra_context or {})

        return TemplateResponse(request, [
            "admin/%s/%s/readonly.html" % (app_label, opts.object_name.lower()),
            "admin/%s/readonly.html" % app_label,
            "admin/readonly.html"
        ], context, current_app=self.admin_site.name)


    def response_post_save_change(self, request, obj):
        """
        Figure out where to redirect after the 'Save' button has been pressed
        when editing an existing object.
        """
        opts = self.model._meta
        if self.has_change_permission(request, None):
            ## originally 'admin:%s_%s_changelist', added obj.pk as argument for view
            post_url = reverse('admin:%s_%s_readonly' %
                               (opts.app_label, opts.module_name),
                               args=(obj.pk,),
                               current_app=self.admin_site.name)
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, post_url)
        else:
            post_url = reverse('admin:index',
                               current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def response_post_save_add(self, request, obj):
        """
        Figure out where to redirect after the 'Save' button has been pressed
        when adding a new object.
        """
        opts = self.model._meta
        post_url = reverse('admin:%s_%s_readonly' %
                           (opts.app_label, opts.module_name),
                           args=(obj.pk,),
                           current_app=self.admin_site.name)
        preserved_filters = self.get_preserved_filters(request)
        post_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, post_url)
        return HttpResponseRedirect(post_url)

    def showEdit(self, obj):
        """Small Edit Button for a direct link to Change dialog"""
        url = obj.get_absolute_url_edit()
        r = '<a href="%s" title="Jump to editing form"><img src="%s"/></a>'\
            % (url, ST.static('img/edit-icon.png'))
        return mark_safe(r)

    showEdit.allow_tags = True
    showEdit.short_description = ''


    def showComments(self, obj):
        """Show comment icon (or nothing if none) depending on rating."""
        url = obj.get_absolute_url() + '#comments'
        r = commenttags.comment_info_icon(obj, url=url)
        return mark_safe(r)
    
    showComments.allow_tags = True
    showComments.short_description = ''
