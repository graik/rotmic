## Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013 Raik Gruenberg

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
from django.contrib import admin
from django.db.models.query import QuerySet as Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

import rotmic.models as M

class CategoryListFilter( admin.SimpleListFilter):
    """
    Provide filter for DnaComponentType.category (all root types)
    """
    title = 'Category'
    parameter_name = 'category'
    
    _class = None

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        categories = self._class.objects.filter(subTypeOf=None)
        return ( (c.name, c.name) for c in categories )
    

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        q = queryset
        
        if not self.value():
            return q
        
        return q.filter(componentType__subTypeOf__name=self.value())


class TypeListFilter( admin.SimpleListFilter):
    """
    Provide filter for DnaComponentType (the actual "second level" type).
    
    This filter has one cosmetic problem, which is that it's setting is not
    automatically deleted if the category filter is changed. I tried but the
    request and queryset are all immutable. Instead, the queryset method is 
    checking for any missmatch between category and filter name and filtering
    is ignored if the category name doesn't match the current subType name.
    """
    title = 'Type'
    parameter_name = 'type'
    
    _class = None
    
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        if not u'category' in request.GET:
            return ()
        
        category_name = request.GET[u'category']
        types = self._class.objects.filter(subTypeOf__name=category_name)
        return ( (t.name, t.name) for t in types )
    
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not u'category' in request.GET:
            return queryset
        
        category = request.GET[u'category']
        subtypes = self._class.objects.filter(subTypeOf__name=category)
        
        r = queryset.filter(componentType__subTypeOf__name=category)
        
        if not self.value():
            return r
        
        ## special case: missmatch between subtype and category
        ## which happens after switching the category
        if len(subtypes.filter(name=self.value())) == 0:
            return r
        
        return r.filter(componentType__name=self.value())


class DnaCategoryListFilter( CategoryListFilter ):
    _class = M.DnaComponentType

class DnaTypeListFilter( TypeListFilter ):
    _class = M.DnaComponentType

class CellCategoryListFilter( CategoryListFilter ):
    _class = M.CellComponentType
    
class CellTypeListFilter( TypeListFilter ):
    _class = M.CellComponentType
    

class RackLocationFilter( admin.SimpleListFilter ):
    """
    Custom Admin Filter for locations in Rack ChangeList.
    The 'parameter_name' is shortened to 'location' rather than the default
    'location__id__exact' and only those locations are displayed that actually
    have any containers in them.
    Entries are selected by pk (ID).
    """
    title = 'Location'
    parameter_name = 'location'
    
    def lookups(self, request, model_admin):
        ## filter for only those locations that contain containers
        locations = M.Location.objects.exclude(racks__isnull=True)
        return ( (o.pk, o.__unicode__()) for o in locations )
    
    def queryset(self, request, queryset):
        q = queryset
        if not self.value():
            return q
        return q.filter(location__id=self.value())
    

class ContainerLocationFilter( admin.SimpleListFilter ):
    """
    Custom Admin Filter for Locations in Container ChangeList.
    The 'parameter_name' is shortened to 'location' rather than the default
    'location__id__exact' and only those locations are displayed that actually
    have any containers in them.
    Entries are selected by pk (ID).
    """    
    title = 'Location'
    parameter_name = 'location'
    
    def lookups(self, request, model_admin):
        ## filter for only those locations that contain containers
        containers = M.Container.objects.all()
        locations = M.Location.objects.filter(racks__containers__in=containers).distinct()
        return ( (o.pk, o.__unicode__()) for o in locations )
    
    def queryset(self, request, queryset):
        q = queryset
        if not self.value():
            return q
        return q.filter(rack__location__id=self.value())
    
    
class ContainerRackFilter( admin.SimpleListFilter ):
    """
    Connects to ContainerLocationFilter. Shows all (non-empty) racks within
    selected Location.
    Entries are selected by pk (ID).
    """
    title = 'Rack'
    parameter_name = 'rack'
    
    def lookups(self, request, model_admin):
        if not u'location' in request.GET:
            return ()
        location_id = request.GET[u'location']
        
        racks = M.Rack.objects.filter(location=location_id)
        ## filter for only those racks that contain any containers
        racks = racks.exclude( containers__isnull=True )
        return ( (r.id, r.__unicode__()) for r in racks )    
    
    def queryset(self, request, queryset):
        if not u'location' in request.GET:
            return queryset
        
        location_id = request.GET[u'location']
        racks = M.Rack.objects.filter(location=location_id)
        
        r = queryset.filter(rack__location=location_id)
        
        if not self.value():
            return r
        
        ## special case: missmatch between current rack and location
        ## which happens after switching the location
        if len(racks.filter(id=self.value())) == 0:
            return r
        
        return r.filter(rack=self.value())

    
class SampleLocationFilter( admin.SimpleListFilter ):
    """
    Modified Admin Filter for Sample locations.
    Entries are selected by displayId.
    """
    title = 'Location'
    parameter_name = 'location'
    _sampleClass = M.Sample
    
    
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        ## filter for only those locations that contain the correct type of samples
        samples = self._sampleClass.objects.all()
        locations = M.Location.objects.filter(racks__containers__samples__in=samples).distinct()

        return ( (o.displayId, o.__unicode__()) for o in locations )
    
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        q = queryset
        if not self.value():
            return q
        return q.filter(container__rack__location__displayId=self.value())

class DnaSampleLocationFilter( SampleLocationFilter ):
    _sampleClass = M.DnaSample
    
class CellSampleLocationFilter( SampleLocationFilter ):
    _sampleClass = M.CellSample

class OligoSampleLocationFilter( SampleLocationFilter ):
    _sampleClass = M.OligoSample


class SampleRackFilter( admin.SimpleListFilter ):
    """Modified Filter for Sample Racks,  responds to SampleLocationListFilter"""
    title = 'Rack'
    parameter_name = 'rack'
    _sampleClass = M.Sample
    
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        if not u'location' in request.GET:
            return ()
        
        location_id = request.GET[u'location']
        racks = M.Rack.objects.filter(location__displayId=location_id)
 
        ## filter for only those racks that contain the correct type of samples
        samples = self._sampleClass.objects.filter(container__rack__location__displayId=location_id)
        racks = racks.filter(containers__samples__in=samples).distinct()  
 
        return ( (r.displayId, r.__unicode__()) for r in racks )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not u'location' in request.GET:
            return queryset
        
        location_id = request.GET[u'location']
        racks = M.Rack.objects.filter(location__displayId=location_id)
        
        r = queryset.filter(container__rack__location__displayId=location_id)
        
        if not self.value():
            return r
        
        ## special case: missmatch between current rack and location
        ## which happens after switching the location
        if len(racks.filter(displayId=self.value())) == 0:
            return r
        
        return r.filter(container__rack__displayId=self.value())
    
class DnaSampleRackFilter( SampleRackFilter ):
    _sampleClass = M.DnaSample
    
class CellSampleRackFilter( SampleRackFilter ):
    _sampleClass = M.CellSample

class OligoSampleRackFilter( SampleRackFilter ):
    _sampleClass = M.OligoSample


class SampleContainerFilter( admin.SimpleListFilter ):
    """Modified Filter for Sample Containers, responds to SampleRackListFilter"""
    title = 'Container'
    parameter_name = 'container'
    _sampleClass = M.Sample
    
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        if not (u'rack' in request.GET and u'location' in request.GET):
            return ()
        
        rack_id = request.GET[u'rack']
        containers = M.Container.objects.filter(rack__displayId=rack_id)

        ## filter for only those containers that contain the correct type of samples
        samples = self._sampleClass.objects.filter(container__rack__displayId=rack_id)
        containers = containers.filter(samples__in=samples).distinct()
        
        return ( (r.displayId, u'%s (%s)' % (r.displayId, r.name)) for r in containers )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not u'rack' in request.GET:
            return queryset
        
        rack_id = request.GET[u'rack']
        containers = M.Container.objects.filter(rack__displayId=rack_id)
        
        r = queryset.filter(container__rack__displayId=rack_id)
        
        if not self.value():
            return r
        
        ## special case: missmatch between current rack and location
        ## which happens after switching the location
        if len(containers.filter(displayId=self.value())) == 0:
            return r
        
        return r.filter(container__displayId=self.value())

class DnaSampleContainerFilter( SampleContainerFilter ):
    _sampleClass = M.DnaSample
    
class CellSampleContainerFilter( SampleContainerFilter ):
    _sampleClass = M.CellSample
    
class OligoSampleContainerFilter( SampleContainerFilter ):
    _sampleClass = M.OligoSample

    
class SortedUserFilter( admin.SimpleListFilter ):
    """
    User Admin Filter for Component tables (registeredBy field),
    sorted by user name rather than id
    
    Hints taken from: 
    http://stackoverflow.com/questions/16560055/django-admin-sorting-list-filter
    """
    title='Author'
    parameter_name = 'user'
    
    user_field = 'registeredBy'  ## override if needed
    
    def lookups(self, request, model_admin):
        qs = model_admin.queryset(request)
        users = User.objects.filter(id__in=qs.values_list(self.user_field, flat=True))
        current = request.user

        ## all except current user
        users = users.distinct().order_by('username').exclude(id=current.id)
        r = [(u.username, u.username) for u in users]

        ## put current user first
        r = [(current.username, 'Me (%s)'%current.username)] + r
        return r
   
   
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(registeredBy__username__exact=self.value())

    