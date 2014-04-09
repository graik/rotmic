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
import StringIO
import Bio.SeqIO as SeqIO

from collections import OrderedDict
import colorsys

class GenbankError(ValueError):
    pass

class GenbankInMemory:
    """
    Creates the following fields:
    
    * sequence: str
    * name: str, genbank name
    * description: str,
    * features: list of dict:
        [ 
           {'name' : str, label or product or gene qualifier or otherwise type string,
            'start': int, start position (starting with 1, not 0 -- SBOL biostart)
            'end'  : int, end position (including, ending with length -- SBOL bioend)
            'type' : str, type string
            'strand': int, -1, 1, 0 as in genbank
            'color': str, HTML color code, a unique color is generated for each unique type string
           }
        ]
    * gb: str, the original genbank record passed in
    * typecolors: dict, {'typestring' : 'colorcode'}  ... as used for features
    """
    
    def __init__(self, gbrecord):
        """@param gbrecord - str, single gb record as string (not file)"""
        self.gb = gbrecord
        self.sequence = ''
        self.features = []
        self.name = ''
        self.description = ''
        self.typecolors = OrderedDict()  ## dictionary of all different feature types : color
        self.parse()
    
    def parse(self):
        try:
            f = StringIO.StringIO( self.gb )
            seqrecord = SeqIO.parse( f, 'gb' ).next()
            self.sequence = seqrecord.seq.tostring()
            self.name = seqrecord.name
            self.description = seqrecord.description
            
            for f in seqrecord.features:
                try:
                    d = self.featureToDict(f)
                    self.features += [ d ]
                    self.typecolors[ d['type'] ] = ''
                except:
                    pass
            
            self.assignTypeColors()
            
        except StopIteration:
            msg = 'Empty or corrupted genbank record'
            raise GenbankError(msg)
        except ValueError, why:
            msg = 'Error reading genbank file: %r' % why
            raise GenbankError(msg)

    def extractName(self, feature):
        """Names/Labels seem to be a mess; make a good guess"""
        q = feature.qualifiers
        r = q.get('label','') or q.get('product','') or q.get('gene') \
            or feature.type
        if r == feature.type:
            print 'fallback to type: ', q
        if type(r) is list:
            r = r[0]
        return r

    def featureToDict(self, feature):
        """
        Convert Bio.SeqFeature to plain dict
        Try to guess reasonable defaults for strand and name
        """
        r = {}
        r['strand'] = feature.strand or 1
        r['start'] = feature.location.start.position + 1  ## to conform to SBOL / Benchling numbering
        r['end'] = feature.location.end.position
        r['name'] = self.extractName(feature)
        r['type'] = feature.type
        print r
        return r

    def colorSpectrum(self, n):
        """
        create a HTML color code spectrum
        see: http://www.gossamer-threads.com/lists/python/python/819538
        """
        sat = 1
        value = 1
        spectrum = []
        
        for x in range(0, n ):
            hue = x / float(n)
            color = list(colorsys.hsv_to_rgb(hue, sat, value))
            for i in range(3):
                color[i] = int(color[i] * 255)
            hexval = ("#%02x%02x%02x" % tuple(color)).upper()
            spectrum += [ hexval ]
        
        return spectrum
    
    def assignTypeColors(self):
        """collect all unique type codes and assign color to each feature"""
        n = len(self.typecolors)
        spectrum = self.colorSpectrum(n)
        assert len(spectrum) == n
        
        ## first assign a color code to all unique Type strings
        for key, color in zip(self.typecolors.keys(), spectrum):
            self.typecolors[key] = color
        
        ## now add color field to each feature according to its type string
        for f in self.features:
            f['color'] = self.typecolors[f['type']]
