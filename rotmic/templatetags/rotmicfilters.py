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

import markdown2
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
@stringfilter
def convertTxt(value):
    """Convert text with Markdown syntax into HTML"""
    return mark_safe(markdown2.markdown(force_unicode(value)))

register.filter('markdown', convertTxt)

@stringfilter
def fasta( seq, name='', block=80, upper=False):
    """
    Format a sequence into a fasta format
    @param seq: sequence
    @type  seq: str
    @param name: name to be used for header ('>name') [None]
    @type  name: str
    @param upper: capitalize letters
    @type  upper: bool
    """
    if upper:
        seq = seq.upper()
    r = ''
    n_chunks = int( len( seq ) / block )

    if name:
        r += '>%s\n' % name

    for i in range(0, n_chunks+1):

        if i * block + block < len( seq ):
            chunk = seq[i * block : i * block + block] + '\n'
        else:
            chunk = seq[i * block :]

        r += chunk

    return  r

register.filter('fasta', fasta)

@register.filter(is_safe=True)
@stringfilter
def markcode(value):
    """Mark a given text input as code"""
    lines = value.split('\n')
    lines = [ '    ' + l for l in lines ]
    r = '\n'.join( lines )
    return convertTxt( r )

register.filter('markcode', markcode )