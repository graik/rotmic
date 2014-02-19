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

class ImportError( Exception ):
    pass

class ImportXls(object):
    """
    Import of Component objects from Excel table (pseudo-abstract base class)
    """
    
    dataForm = F.DnaComponentForm
    
    modelClass = M.DnaComponent
       
    # rename Excel headers to field name (dict)
    xls2field = { 'id' : 'displayId',
                  'type' : 'componentType',
                }
    
    # lookup instructions for fields (default: model=DnaComponent,
    # targetfield=displayId) (list of dict)
    xls2foreignkey = [ ]
    
    # lookup instructions for Many2Many fields (list of dict)
    xls2many = [ ]
                       
    
    def __init__(self, f, user, request=None):
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
        self.request = request
        
        self.objects = []

        
    def parse(self, keyrow=0, firstrow=1 ):
        """
        Extract field names from |keyrow| and extract data for each field from
        excel workbook starting at row |firstrow|.
        @param keyrow: int, row containing field names
        @param firstrow: int, first row containing data
        @return: [ {} ], list of dictionaries 
        """
        try:
            book = X.open_workbook( self.f )
            sheet= book.sheets()[0]
    
            firstrow -= 1
            keys = []
            ## iterate until there is a row with at least 3 non-empty values
            while len([k for k in keys if k]) < 3:
                keys = sheet.row_values(firstrow) ## extract labels from header row
                firstrow += 1
    
            if not keys:
                raise ImportError, 'Could not identify table header row.'
                
            r = []
            for row in range( firstrow, sheet.nrows ):
                values = sheet.row_values( row )
    
                ## ignore rows with empty first column
                if values[0]:
                    r += [ dict( zip( keys, values ) ) ] 
            
            self.rows = r
            
            return r

        except Exception as e:
            raise ImportError('Something went terribly wrong during parsing of the file: '+\
                              unicode(e))
        return []
    

    def renameKey( self, d, key, newkey):
        if key in d:
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
        
        for key, value in self.xls2field.items():
            self.renameKey(d, key, value )
        
        return d

    def __dbfetchSingle(self, model, **kwarg ):
        matches = model.objects.filter( **kwarg )
        if len( matches ) == 1:
            return matches[0].id
        return None
        

    def __lookupId(self, value, model=M.DnaComponent, targetfield='displayId', 
                   targetfield2=None ):
        """Convert unique field value into ID for a model instance"""
        error, r = None, None
        try:
            value = value.strip()
            
            if not value:
                return value, error
        
            kwarg = { targetfield : value }
            r = self.__dbfetchSingle( model, **kwarg )
    
            if r is None and targetfield2:
                kwarg = { targetfield2 : value }
                r = self.__dbfetchSingle( model, **kwarg )
            
            if r is None:
                raise model.DoesNotExist(\
                    'Cannot find entry with queries %r or %r' %\
                    ({ targetfield : value }, { targetfield2 : value }) )
            
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
    
    
    def __lookupMany(self, d, field='', model=M.DnaComponent, 
                     targetfield='displayId', targetfield2=None ):
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
                x, e = self.__lookupId(v, model=model, targetfield=targetfield,
                                       targetfield2=targetfield2 )
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

        for x in self.xls2foreignkey:
            self.__lookup( d, **x )

        for x in self.xls2many:
            self.__lookupMany( d, **x )
        
        return d


    def postprocessDict( self, d ):
        """
        Add fields to dict after cleanup and forgeignKey lookup
        """
        d['registeredBy'] = self.user.id
        d['registeredAt'] = datetime.datetime.now()
        d['modifiedAt'] = datetime.datetime.now()
        d['modifiedBy'] = self.user.id

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
                form.request = self.request  ##This is actually only required for forms derrived from SampleForm
                
                valid = form.is_valid()
                
                ## inline forms for provenance would need to be created separately here.
                
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
        


class ImportXlsComponent( ImportXls ):
    """Base class for Component-derrived import."""
    
    # rename Excel headers to field name (dict)
    xls2field = { 'id' : 'displayId',
                  'type' : 'componentType',
                }
    
    typeClass = M.ComponentType  ## abstract base class

    def generateName(self, d):
        """If missing, compose name from insert and vectorbackbone"""
        ## automatically create name
        try:
            pass
        except Exception as e:
            d['errors']['name'] = [u'Error generating name from insert and vector: '+unicode(e)]
        

    def correctStatus(self, d):
        """Replace human-readable status by internal status value"""
        choices = self.modelClass.STATUS_CHOICES

        human2system = { x[1] : x[0] for x in choices }

        status = d.get('status', None)
        ## replace only if listed as key in human to system map
        d['status'] = human2system.get(status, status)

    
    def setCategory(self, d):
        """Extract category from componentType"""
        try:
            t = self.typeClass.objects.get( id=d['componentType'])
            d['componentCategory'] = t.category().id
        except Exception as e:
            d['errors']['componentType'] = d['errors'].get('componentType', [])
            d['errors']['componentType'].append( unicode(e) )

    def postprocessDict( self, d ):
        """
        Add fields to dict after cleanup and forgeignKey lookup
        """
        d = super(ImportXlsComponent, self).postprocessDict(d)

        ## set category
        self.setCategory(d)
        self.generateName(d)
        self.correctStatus(d)
        
        return d
    
    def cleanType( self, d):
        """
        Remove category from type string. Example:
        'Plasmid / generic plasmid' -> 'generic plasmid'
        @param d - dict with field information for one entry (after cleaning)
        """
        value = d.get('componentType', '')
        
        try:    
            if '/' in value:
                d['componentType'] = value[ value.index('/')+1 : ].strip()
        except ValueError:
            pass
    
    def cleanDict(self, d):
        """Add componentType string cleaning."""
        super(ImportXlsComponent,self).cleanDict(d)
        self.cleanType(d)
        return d


class ImportXlsDna( ImportXlsComponent ):
    """DNA construct import"""
    
    dataForm = F.DnaComponentForm
    
    modelClass = M.DnaComponent
    
    typeClass = M.DnaComponentType
    
    # rename Excel headers to field name
    xls2field = { 'id' : 'displayId',
                  'type' : 'componentType',
                  'vector' : 'vectorBackbone' }
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = [ { 'field' : 'insert' },
                       { 'field' : 'vectorBackbone' },
                       { 'field' : 'componentType', 'model' : M.DnaComponentType,
                         'targetfield' : 'name'}
                       ]
    
    # lookup instructions for Many2Many fields
    xls2many = [ { 'field' : 'markers', 
                   'model' : M.DnaComponent, 'targetfield' : 'displayId',
                   'targetfield2' : 'name' } 
                 ]

    def generateName(self, d):
        """If missing, compose name from insert and vectorbackbone"""
        ## automatically create name
        try:
            if not d.get('name', '') and d.get('vectorBackbone','') and d.get('insert',''):
                vector = M.DnaComponent.objects.get( id=d['vectorBackbone'])
                insert = M.DnaComponent.objects.get( id=d['insert'])
                
                d['name'] = insert.name + '_' + vector.name

        except Exception as e:
            d['errors']['name'] = [u'Error generating name from insert and vector: '+unicode(e)]

        

class ImportXlsCell( ImportXlsComponent ):
    """Modifed cell import"""
    
    dataForm = F.CellComponentForm
    
    typeClass = M.CellComponentType
    
    modelClass = M.CellComponent
    
    # rename Excel headers to field name
    xls2field = { 'id' : 'displayId',
                  'strain' : 'componentType' }
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = [ { 'field' : 'plasmid' },
                       { 'field' : 'componentType', 'model' : M.CellComponentType,
                         'targetfield' : 'name'}
                       ]
    
    # lookup instructions for Many2Many fields
    xls2many = [ { 'field' : 'markers', 
                   'model' : M.DnaComponent, 'targetfield' : 'displayId',
                   'targetfield2' : 'name' } 
                 ]
    
    def generateName(self, d):
        """If missing, compose name from plasmid and cell"""
        ## automatically create name
        try:
            if not d.get('name', '') and d.get('plasmid',''):
                plasmid = M.DnaComponent.objects.get( id=d['plasmid'])
                cell = M.CellComponentType.objects.get( id=d['componentType'])
                
                d['name'] = plasmid.name + '@' + cell.name

        except Exception as e:
            d['errors']['name'] = [u'Error generating name from plasmid and cell: '+unicode(e)]



class ImportXlsOligo( ImportXlsComponent ):
    """Oligo import"""
    
    dataForm = F.OligoComponentForm
    
    typeClass = M.OligoComponentType
    
    modelClass = M.OligoComponent
    
    # rename Excel headers to field name
    xls2field = { 'id' : 'displayId',
                  'type' : 'componentType',
                  'tm in c' : 'meltingTemp',
                  'tm' : 'meltingTemp',
                  'dna templates' : 'templates'}
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = [  { 'field' : 'componentType', 'model' : M.OligoComponentType,
                         'targetfield' : 'name'}
                       ]
    
    # lookup instructions for Many2Many fields
    xls2many = [ { 'field' : 'templates', 
                   'model' : M.DnaComponent, 'targetfield' : 'displayId' } 
                 ]
                
    def postprocessDict(self, d):
        """Enforce integer melting temperatures"""
        d = super(ImportXlsOligo, self).postprocessDict(d)
        
        try:
            if d.get('meltingTemp',None):
                d['meltingTemp'] = int(d['meltingTemp'])
        except Exception as e:
            d['errors']['meltingTemp'] = d['errors'].get('meltingTemp', [])
            d['errors']['meltingTemp'].append( unicode(e) )
    
        return d
    

class ImportXlsChemical( ImportXlsComponent ):
    """Chemical import"""
    
    dataForm = F.ChemicalComponentForm
    
    typeClass = M.ChemicalType
    
    modelClass = M.ChemicalComponent
    
    # rename Excel headers to field name
    xls2field = { 'id' : 'displayId',
                  'type' : 'componentType',
                  'c.a.s.' : 'cas' }
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = [  { 'field' : 'componentType', 'model' : M.ChemicalType,
                         'targetfield' : 'name'}
                       ]
    

class ImportXlsLocation( ImportXls ):
    """Import location records from table"""
    dataForm = F.LocationForm
    
    modelClass = M.Location
    
    # rename Excel headers to field name
    xls2field = { 'id' : 'displayId' }
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = []
        
    def postprocessDict(self, d):
        d = super(ImportXlsLocation, self).postprocessDict(d)
        
        try:
            if d.get('temperature',None):
                d['temperature'] = int(d['temperature'])
        except Exception as e:
            d['errors']['temperature'] = d['errors'].get('temperature', [])
            d['errors']['temperature'].append( unicode(e) )

        try:
            if type(d.get('room', '')) is float:
                d['room'] = int(d['room'])
        except Exception as e:
            d['errors']['room'] = d['room'].get('room', [])
            d['errors']['room'].append( unicode(e) )
            
        return d
    
    
class ImportXlsRack( ImportXls ):
    dataForm = F.RackForm
    
    modelClass = M.Rack
    
    # rename Excel headers to field name
    xls2field = { 'id' : 'displayId' }
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = [  { 'field' : 'location', 'model' : M.Location,
                         'targetfield' : 'displayId'}
                       ]
    

class ImportXlsContainer( ImportXls ):
    """Excel Import of Containers"""
    
    dataForm = F.ContainerForm
    
    modelClass = M.Container
    
    # rename Excel headers to field name
    xls2field = { 'id' : 'displayId',
                  'type' : 'containerType' }
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = [  { 'field' : 'rack', 
                          'model' : M.Rack,
                          'targetfield' : 'displayId'},
                       ]
    ## ToDo include type code cleanup
    

class ImportXlsSample( ImportXls ):
    """Base class for different Sample imports"""
    
    # rename Excel headers to field name
    xls2field = { 'id' : 'displayId',
                  'position' : 'displayId',
                  'prepared' : 'preparedAt',
                  'aliquots' : 'aliquotNr',
                  'in buffer': 'solvent',
                  'concentration unit' : 'concentrationUnit',
                  'amount unit' : 'amountUnit',
                  'experiment #' : 'experimentNr'}
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = [  { 'field' : 'container', 'model' : M.Container },

                        { 'field' : 'concentrationUnit', 'model' : M.Unit,
                          'targetfield' : 'name'},
                        { 'field' : 'amountUnit', 'model' : M.Unit,
                          'targetfield' : 'name'},

                       ]
    

    def correctStatus(self, d):
        """Replace human-readable status by internal status value"""
        choices = self.modelClass.STATUS_CHOICES

        human2system = { x[1] : x[0] for x in choices }

        status = d.get('status', None)
        ## replace only if listed as key in human to system map
        d['status'] = human2system.get(status, status)

    def postprocessDict( self, d ):
        """Add fields to dict after cleanup and forgeignKey lookup"""
        d = super(ImportXlsSample, self).postprocessDict(d)

        self.correctStatus(d)
        return d


class ImportXlsDnaSample( ImportXlsSample ):
    """Excel import of DNA samples"""
    dataForm = F.DnaSampleForm
    
    modelClass = M.DnaSample
    
    # rename Excel headers to field name
    xls2field = dict( ImportXlsSample.xls2field, **{'dna construct' : 'dna'})
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = ImportXlsSample.xls2foreignkey + \
                     [ { 'field' : 'dna', 'model' : M.DnaComponent } ]



class ImportXlsOligoSample( ImportXlsSample ):
    """Excel import of Oligo nucleotide samples"""
    dataForm = F.OligoSampleForm
    
    modelClass = M.OligoSample
    
    # rename Excel headers to field name
    xls2field = dict( ImportXlsSample.xls2field, **{'oligo nucleotide' : 'oligo'})
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = ImportXlsSample.xls2foreignkey + \
                     [ { 'field' : 'oligo', 'model' : M.OligoComponent } ]


class ImportXlsChemicalSample( ImportXlsSample ):
    """Excel import of Oligo nucleotide samples"""
    dataForm = F.ChemicalSampleForm
    
    modelClass = M.ChemicalSample
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = ImportXlsSample.xls2foreignkey + \
                     [ { 'field' : 'chemical', 'model' : M.ChemicalComponent } ]


class ImportXlsCellSample( ImportXlsSample ):
    """Excel import of DNA samples"""
    dataForm = F.CellSampleForm
    
    modelClass = M.CellSample
    
    # rename Excel headers to field name
    xls2field = dict( ImportXlsSample.xls2field, **{'modified cell' : 'cell',
                                                    'strain' : 'cellType',
                                                    'in strain' : 'cellType',
                                                    'or plasmid' : 'plasmid'})
    
    # lookup instructions for fields (default model=DnaComponent,
    # targetfield=displayId)
    xls2foreignkey = ImportXlsSample.xls2foreignkey + \
                     [ { 'field' : 'cell', 'model' : M.CellComponent},
                       { 'field' : 'cellType', 'model' : M.CellComponentType, 
                         'targetfield' : 'name'},
                       { 'field' : 'plasmid', 'model' : M.DnaComponent}
                       ]

    def cleanType( self, d):
        """
        Remove category from type string. Example:
        'E. coli / Mach1' -> 'Mach1'
        @param d - dict with field information for one entry (after cleaning)
        """
        value = d.get('cellType', '')
        
        try:    
            if '/' in value:
                d['cellType'] = value[ value.index('/')+1 : ].strip()
        except ValueError:
            pass
    
    def cleanDict(self, d):
        """Add componentType string cleaning."""
        super(ImportXlsCellSample,self).cleanDict(d)
        self.cleanType(d)
        return d
    