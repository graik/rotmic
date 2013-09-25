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

## imports for show / display links
from django.utils.safestring import mark_safe

from functools import update_wrapper, partial
csrf_protect_m = method_decorator(csrf_protect)

## imports for overriding ChangeList
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.util import quote

## Objec-level permission integration in Admin
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_objects_for_user

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
    

class ViewFirstModelAdmin( GuardedModelAdmin ):
    """
    Custom version of admin.ModelAdmin which shows a read-only
    View for a given object instead of the normal ChangeForm. The changeForm
    is accessed by admin/ModelName/id/edit
    
    Also has custom code to filter admin for django-guardian permissions. However,
    this is still incomplete and needs to be re-written. E.g. a user is not given
    access to it's own objects and groups don't seem to be supported. The only
    thing that works out of the box is the assigmnent of row-level permissions.
    """
    
    ## reset to ModelAdmin default (de-activates Guardian template)
    change_form_template = None
    
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
            
            # django-guardian views
            url(r'^(?P<object_pk>.+)/edit/permissions/$',
                view=self.admin_site.admin_view(self.obj_perms_manage_view),
                name='%s_%s_permissions' % info),
            url(r'^(?P<object_pk>.+)/edit/permissions/user-manage/(?P<user_id>\-?\d+)/$',
                view=self.admin_site.admin_view(
                    self.obj_perms_manage_user_view),
                name='%s_%s_permissions_manage_user' % info),
            url(r'^(?P<object_pk>.+)/edit/permissions/group-manage/(?P<group_id>\-?\d+)/$',
                view=self.admin_site.admin_view(
                    self.obj_perms_manage_group_view),
                name='%s_%s_permissions_manage_group' % info),
            
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
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_text(opts.verbose_name), 'key': escape(object_id)})
        
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
        else:
            post_url = reverse('admin:index',
                               current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)


    ## following code taken from 
    ## http://stackoverflow.com/questions/10928860/objects-with-permissions-assigned-by-django-guardian-not-visible-in-admin
    def queryset(self, request):
        qs = super(ViewFirstModelAdmin, self).queryset(request)
        # Check global permission
        if super(ViewFirstModelAdmin, self).has_change_permission(request) \
            or (not self.list_editable and self.has_view_permission(request)):
                return qs
        # No global, filter by row-level permissions. also use view permission if the changelist is not editable
        if self.list_editable:
            return get_objects_for_user(request.user, [self.opts.get_change_permission()], qs)
        else:
            return get_objects_for_user(request.user, [self.opts.get_change_permission(), self.get_view_permission(
)], qs, any_perm=True)

    def has_change_permission(self, request, obj=None):
        if super(ViewFirstModelAdmin, self).has_change_permission(request, obj):
            return True
        if obj is None:
            # Here check global 'view' permission or if there is any changeable items
            return self.has_view_permission(request) or self.queryset(request).exists()
        else:
            # Row-level checking
            return request.user.has_perm(self.opts.get_change_permission(), obj)

    def get_view_permission(self):
        return 'view_%s' % self.opts.object_name.lower()

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm(self.opts.app_label + '.' + self.get_view_permission(), obj)

    def has_delete_permission(self, request, obj=None):
        return super(ViewFirstModelAdmin, self).has_delete_permission(request, obj) \
                or (obj is not None and request.user.has_perm(self.opts.get_delete_permission(), obj))
        


class ComponentModelAdmin( ViewFirstModelAdmin ):
    """
    Derived from ViewFirstModelAdmin -- Custom version of admin.ModelAdmin
    which shows a read-only View for a given object instead of the normal
    ChangeForm. The changeForm is accessed by admin/ModelName/id/edit.
    
    In addition, there is extra_context provided to the change_view:
    * dnaTypes -- all registered instances of DnaComponentType
    * cellTypes -- all CellComponentTypes
    * dnaCategories -- all "super" or base-level DnaComponentTypes
    * cellCategories -- all "super" or base-level CellComponentTypes
    
    Component-specific methods:
    * showComment -- truncated comment with html mouse-over full text for tables
    """
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        "The 'Edit' admin view for this model."
        extra_context = extra_context or {}
        
        extra_context['dnaTypes'] = M.DnaComponentType.objects.all()
        extra_context['dnaCategories'] = M.DnaComponentType.objects.filter(subTypeOf=None)
        extra_context['cellTypes'] = M.CellComponentType.objects.all()
        extra_context['cellCategories'] = M.CellComponentType.objects.filter(subTypeOf=None)
        
        return super(ComponentModelAdmin, self).change_view(\
            request, object_id, form_url, extra_context=extra_context)


    def add_view(self, request, form_url='', extra_context=None):
        "The 'Add new' admin view for this model."
        extra_context = extra_context or {}
        
        extra_context['dnaTypes'] = M.DnaComponentType.objects.all()
        extra_context['dnaCategories'] = M.DnaComponentType.objects.filter(subTypeOf=None)
        extra_context['cellTypes'] = M.CellComponentType.objects.all()
        extra_context['cellCategories'] = M.CellComponentType.objects.filter(subTypeOf=None)
        
        return super(ComponentModelAdmin, self).add_view(\
            request, form_url, extra_context=extra_context)

    def showComment(self, obj):
        """
        @return: str; truncated comment with full comment mouse-over
        """
        if not obj.comment: 
            return u''
        if len(obj.comment) < 40:
            return unicode(obj.comment)
        r = unicode(obj.comment[:38])
        r = '<a title="%s">%s</a>' % (obj.comment, F.truncate(obj.commentText(), 40))
        return r
    showComment.allow_tags = True
    showComment.short_description = 'Description'
    
    def showEdit(self, obj):
        """Small Edit Button for a direct link to Change dialog"""
        return mark_safe('<a href="%s"><img src="http://icons.iconarchive.com/icons/custom-icon-design/office/16/edit-icon.png"/></a>'\
                         % (obj.get_absolute_url_edit() ) )
    showEdit.allow_tags = True    
    showEdit.short_description = 'Edit'     

    def showStatus(self, obj):
        color = {u'available': '088A08', # green
                 u'planning': '808080', # grey
                 u'construction' : '0000FF', # blue
                 u'abandoned': 'B40404', # red
                 }
        return '<span style="color: #%s;">%s</span>' %\
               (color.get(obj.status, '000000'), obj.status)
    showStatus.allow_tags = True
    showStatus.short_description = 'Status'
