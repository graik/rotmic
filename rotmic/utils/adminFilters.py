from django.contrib import admin
from django.db.models.query import QuerySet as Q

from rotmic.models import DnaComponentType, CellComponentType


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
    _class = DnaComponentType


class DnaTypeListFilter( TypeListFilter ):
    _class = DnaComponentType

class CellCategoryListFilter( CategoryListFilter ):
    _class = CellComponentType
    
class CellTypeListFilter( TypeListFilter ):
    _class = CellComponentType