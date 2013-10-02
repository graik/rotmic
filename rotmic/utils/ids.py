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
"""Auto-generation of displayIds"""

import rotmic.models as M
from django.contrib.auth.models import User

import re

def suggestId(componentClass, prefix):
    objects = componentClass.objects.filter( displayId__startswith=prefix )

    if objects.count() == 0:
        return '%s%04i' % (prefix, 1)
    pattern = re.compile(prefix+'([0-9]+)')
    matches = [ pattern.match( o.displayId ) for o in objects ]
    numbers = [ int(x.groups()[0]) for x in matches if x is not None ]
    numbers.sort()
    
    return '%s%04i' % (prefix, numbers[-1]+1)

def suggestDnaId(user_id, prefix='', middle=''):
    """
    user_id - int, pk of User object
    prefix  - str, first characters of desired DNA ID (default: from user.profile)
    middle  - str, additional prefix characters (e.g. "p" for plasmid, default: '')
    """
    user = User.objects.get( id=user_id )
    prefix = prefix or user.profile.dcPrefix or user.profile.prefix
    prefix += middle

    return suggestId( M.DnaComponent, prefix )