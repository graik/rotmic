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
"""Bulk import of records from XLS and/or CSV files"""
import tempfile, datetime, re

import xlrd as X
import django.core.files.uploadedfile as U

import rotmic.models as M
import rotmic.forms as F

class ImportXls:
    
    dataForm = F.DnaComponentForm
    
    def __init__(self, f, user):
        """
        @param f: file handle pointing to Excel file
        @param user: django.auth.models.User instance
        """
        if isinstance(f, U.File):
            fname = tempfile.mktemp(prefix='rotmicupload_')
            ftemp = open(fname, 'w')
            ftemp.writelines( f.readlines() )
            ftemp.close()
            f = fname
            
        self.f = f
        self.user = user
        
        self.objects = []

        
    def parse(self, keyrow=0, firstrow=1 ):
        """
        Extract field names from |keyrow| and extract data for each field from
        excel workbook starting at row |firstrow|.
        @param keyrow: int, row containing field names
        @param firstrow: int, first row containing data
        @return: [ {} ], list of dictionaries 
        """
        book = X.open_workbook( self.f )
        sheet= book.sheets()[0]

        keys = sheet.row_values(0) ## extract labels from first row
        
        r = []
        for row in range( firstrow, sheet.nrows ):
            r += [ dict( zip( keys, sheet.row_values( row ) ) ) ] 
        
        self.rows = r
        
        return r
    

    def renameKey( self, d, key, newkey):
        d[newkey] = d[key]
        del d[key]
    
    
    def cleanDict( self, d ):
        """
        Pre-processing of dictionary values (before foreignKey lookup).
        """
        for key in d:
            newKey = key.lower()
            if newKey != key:
                self.renameKey( d, key, newKey )
                
        self.renameKey(d, 'id', 'displayId')
        self.renameKey(d, 'type', 'componentType')
        self.renameKey(d, 'vector', 'vectorBackbone')
        
        return d


    def __lookupId(self, value, model=M.DnaComponent, targetfield='displayId'):
        """Convert unique field value into ID for a model instance"""
        error, r = None, None
        try:
            value = value.strip()
            
            if not value:
                return value, error
        
            kwarg = { targetfield : value }
            r = model.objects.get( **kwarg ).id
        except Exception as e:
            error = unicode(e)
            r = None
        
        return r, error
        

    def __lookup(self, d, field='', model=M.DnaComponent, targetfield='displayId'):
        """
        Lookup a foreign-key object by its name, displayId, etc. The method replaces
        the value of d[field] by the model ID. Errors are recorded
        in d['errors'][field].
        
        @param d: single dict as returned by parse
        @param field: the field in the dict that should be converted
        @param model: the registry data model (table) that should be querried
        @param targetfield: the field within the data model that is used to
                            identify the correct instance
        @return: True if there wasn't any error
        """
        value, error = self.__lookupId( d[field], 
                                        model=model, targetfield=targetfield )
        
        d[field] = value
        if error:
            d['errors'][field] = d['errors'].get(field, [])
            d['errors'][field] = [ error ]
    
    
    def __lookupMany(self, d, field='', model=M.DnaComponent, targetfield='displayId'):
        """
        Lookup Many2Many objects by name, displayId, etc. The method replaces
        the value of d[field] by a list of model IDs. Errors are recorded
        in d['errors'][field].
        
        @param d: single dict as returned by parse
        @param field: the field in the dict that should be converted
        @param model: the registry data model (table) that should be querried
        @param targetfield: the field within the data model that is used to
                            identify the correct instance
        @return: True if there wasn't any error
        """
        try:
            values = d.get(field, '').strip()
            values = values.split(',')
            
            r = []
            errors = []
            for v in values:
                v = v.strip()
                x, e = self.__lookupId(v, model=model, targetfield=targetfield)
                if x:
                    r += [x]
                if e:
                    errors += [e]

        except Exception as e:
            errors += [ unicode(e) ]

        d[field] = r
            
        if errors:
            d['errors'][field] = d['errors'].get(field, [])
            d['errors'][field] += errors


    def lookupRelations(self, d ):
        """
        Convert names or displayIds into db IDs to foreignKey instances.
        """
        d['errors'] = {}
        self.__lookup( d, field='insert', model=M.DnaComponent )
        self.__lookup( d, field='vectorBackbone', model=M.DnaComponent )
        self.__lookup( d, field='componentType', model=M.DnaComponentType,
                       targetfield='name')
        self.__lookupMany( d, field='markers', model=M.DnaComponent )
        
        return d


    def generateName(self, d):
        """If missing, compose name from insert and vectorbackbone"""
        ## automatically create name
        try:
            if not d.get('name', '') and ('vectorBackbone' in d) and ('insert' in d):
                vector = M.DnaComponent.objects.get( id=d['vectorBackbone'])
                insert = M.DnaComponent.objects.get( id=d['insert'])
                
                d['name'] = insert.name + '_' + vector.name

        except Exception as e:
            d['errors']['name'] = [u'error assigning name: '+unicode(e)]
        
    
    def postprocessDict( self, d ):
        """
        Add fields to dict after cleanup and forgeignKey lookup
        """
        d['registeredBy'] = self.user.id
        d['registeredAt'] = datetime.datetime.now()
        d['modifiedAt'] = datetime.datetime.now()
        d['modifiedBy'] = self.user.id
        
        ## set category
        try:
            t = M.DnaComponentType.objects.get( id=d['componentType'])
            d['componentCategory'] = t.category().id
        except Exception as e:
            d['errors']['componentType'] = d['errors'].get('componentType', [])
            d['errors']['componentType'].append( unicode(e) )
        
        self.generateName(d)
        
        return d
    

    def updateErrors( self, d, errors ):
        """
        Append additional errors to entries in d['errors']
        @param d: dict, row dictionary with field : value pairs
        @param errors: dict { 'str' : [ str ] }
        Note: the input errors are assumed to be a list of str (not str).
        """
        r = d['errors']
        
        for k, v in errors.items():
            if k in r:
                r[k].extend( [ x for x in v] ) ## somehow the [...] magically removes HTML tags
            else:
                r[k] = [ x for x in v]

        return r

    def dict2instance( self, d ):
        """
        Create a model instance from a dictionary.
        """
        ## no errors while looking up related fields
        if not d.get('errors', []):
            try:
                form = self.dataForm( data=d )
                valid = form.is_valid()
                
                d['object'] = form.save( commit=False )
                d['object_form'] = form
            except ValueError as e:
                self.updateErrors( d, form._errors )
        
        return d

    
    def getObjects( self ):
        """
        Run all parsing, cleanup and object extraction steps.
        Each returned dict has a key 'object' pointing to a (non-saved) model 
        instance or None, as well as a key 'errors' pointing to a dictionary
        with a list of errors associated to each field (if any).
    
        @return [ dict ]; 
        """
        r = self.parse() ## list of dictionaries with key(heading)-value pairs
        
        self.forms = []
        self.objects = []
        self.failed = []

        for d in r:
            entry = self.lookupRelations( self.cleanDict(d) )
            entry = self.postprocessDict( entry )
            entry = self.dict2instance( entry )
            
            if entry.get('object', None):
                self.objects += [ entry['object'] ]

            if entry.get('object_form', None):
                self.forms += [ entry['object_form'] ]

            if entry['errors']:
                self.failed += [ entry ]
        
    