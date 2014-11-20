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
import sys
import traceback
from inspect import getframeinfo


def lastError():
    """
    Collect type and line of last exception.
    
    @return: '<ExceptionType> in line <lineNumber>:<Exception arguments>'
    @rtype: String
    """
    try:
        trace = sys.exc_info()[2]
        why = sys.exc_info()[1]
        try:
            why = sys.exc_info()[1].args
        except:
            pass
        file = getframeinfo( trace.tb_frame )[0]

        result = "%s in %s line %i:\n\t%s." % ( str(sys.exc_type),
                  file, trace.tb_lineno, str(why) )

    finally:
        trace = None

    return result


def lastErrorTrace( limit=None ):
    tb = sys.exc_info()[2]

    lines = traceback.extract_tb( tb, None )

    result = ''
    for l in lines:
        pyFile = stripFilename( l[0] )
        result += '%s: %i (%s) %s\n' % (pyFile, l[1],l[2],l[3])

    return result
