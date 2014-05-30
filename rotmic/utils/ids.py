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
"""Auto-generation of displayIds"""

import rotmic.models as M
from django.contrib.auth.models import User

import re, string

ex_sampleId = re.compile('([A-Za-z]{0,1})([0-9]+)')
ex_number = re.compile('([0-9]+)')

def _extractNumbers( queryset, pattern ):
    matches = [ pattern.match( o.displayId ) for o in queryset ]
    numbers = [ int(x.groups()[0]) for x in matches if x is not None ]
    numbers.sort()
    return numbers    


def nextId(modelClass, user, category_id=None):
    """Generic ID generator"""
    f = getattr(modelClass, 'nextAvailableId', None)
    if callable(f):
        return f(user, category_id=category_id)
    else:
        return 'xxx'


def __nextSampleInBox( samples ):
    """
    """
    try:
        if not samples.count(): 
            return '01'
        
        numbers = _extractNumbers( samples, ex_number )
        return '%02i' % (numbers[-1] + 1)
    except:
        return ''    


def splitSampleId( sampleId ):
    """
    sampleId - str, like 'A1' or '12'
    @return (str, int) - letter, number
    """
    match = ex_sampleId.match(sampleId)
    if not match:
        return '', None
    
    letter, number = match.groups()
    return letter.upper(), int(number)


def __nextSampleInPlate( samples, columns=12, rows=8 ):
    """
    """
    if not samples.count(): 
        return 'A1'
    assert rows < 26
    
    ids = [ o.displayId for o in samples ]
    ids.sort()

    id_tupples = [ splitSampleId( s ) for s in ids ]
    
    letter, number = id_tupples[-1]
    if number >= columns:
        letter = string.ascii_uppercase[ string.ascii_uppercase.find(letter)+1 ]
        number = 0
    return letter.upper() + '%02i' % (number + 1)
    

def suggestSampleId(container_id):
    """
    container_id - int, pk of parent container
    """
    try:
        box = M.Container.objects.get(id=container_id)
        samples = box.samples.all()
        
        try:
            if box.containerType == '96-well-plate':
                return __nextSampleInPlate( samples )
            if box.containerType == '384-well-plate':
                return __nextSampleInPlate( samples, columns=24, rows=16 )
            else:
                return __nextSampleInBox( samples )
        except:
            return ''
        
    except ValueError:
        return ''
    

