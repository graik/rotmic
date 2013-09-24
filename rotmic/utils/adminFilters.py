from django.contrib import admin
from django.db.models.query import QuerySet as Q

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
    
    
class RackListFilter( admin.SimpleListFilter):
    """
    Provide filter for Racks responding to currently selected Location.
    This filter inter-operates with the un-modified Location filter.
    """
    title = 'Rack'
    parameter_name = 'rack'
    
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        if not u'rack__location__id__exact' in request.GET:
            return ()
        
        location_id = request.GET[u'rack__location__id__exact']
        racks = M.Rack.objects.filter(location=location_id)
        return ( (r.id, r.__unicode__()) for r in racks )
    
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not u'rack__location__id__exact' in request.GET:
            return queryset
        
        location_id = request.GET[u'rack__location__id__exact']
        racks = M.Rack.objects.filter(location=location_id)
        
        r = queryset.filter(rack__location=location_id)
        
        if not self.value():
            return r
        
        ## special case: missmatch between current rack and location
        ## which happens after switching the location
        if len(racks.filter(id=self.value())) == 0:
            return r
        
        return r.filter(rack=self.value())


class SampleLocationListFilter( admin.SimpleListFilter ):
    """Modified Filter for Sample locations"""
    title = 'Location'
    parameter_name = 'location'
    _sampleClass = M.DnaSample
    
    
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


class SampleRackListFilter( admin.SimpleListFilter ):
    """Modified Filter for Sample Racks,  responds to SampleLocationListFilter"""
    title = 'Rack'
    parameter_name = 'rack'
    _sampleClass = M.DnaSample
    
    
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
    
class SampleContainerListFilter( admin.SimpleListFilter ):
    """Modified Filter for Sample Containers, responds to SampleRackListFilter"""
    title = 'Container'
    parameter_name = 'container'
    _sampleClass = M.DnaSample
    
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
        
        return ( (r.displayId, r.__unicode__()) for r in containers )

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