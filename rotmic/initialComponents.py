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
"""
Pre-populate database with components instances that are needed for templates
and pre-defined actions.
"""
from rotmic.models import DnaComponent
import initialTypes as IT

import logging, datetime

from django.contrib.auth.models import User

def getcreate(componentClass=DnaComponent, displayId='', **kwargs):
    """
    Look up component of given name or create a new one and save it to the DB.
    """
    try:
        r = componentClass.objects.get(displayId=displayId)
 
    except componentClass.DoesNotExist:

        superuser = User.objects.filter(is_superuser=True)[0]
        kwargs.update({'registeredBy':superuser,
                       'registeredAt':datetime.datetime.now()})
                       
        r = componentClass( displayId=displayId, **kwargs)
        r.save()
        logging.warning('Created missing type: %s %s.' % (componentClass.__name__, displayId) )

    return r

## Pre-defined DnaComponent(s) required in the project

vectorUnknown = getcreate(displayId='v0000', name='unknown vector',
                          componentType=IT.dcVectorUndefined, status='planning',
                          comment='Default place holder for unknown vector backbones.'\
                          +'\nDo not modify.')