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
import tempfile

import xlrd as X
import django.core.files.uploadedfile as U

class ImportXls:
    
    def __init__(self, f):
        """@param f: file handle pointing to Excel file"""
        if isinstance(f, U.File):
            fname = tempfile.mktemp(prefix='rotmicupload_')
            ftemp = open(fname, 'w')
            ftemp.writelines( f.readlines() )
            ftemp.close()
            f = fname
            
        self.f = f
        
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
        
        return r