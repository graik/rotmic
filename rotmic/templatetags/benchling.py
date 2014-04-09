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
"""
Django template tags for benchling sequence display widget

Use:
   {% load benchling %}
   ...
   {% block extrahead %}{{ block.super }}
    {% benchling_libs %}
   {% endblock %}
   
   {% benchling o %}

Where 'o' is a Dna/ProteinComponent object from the template context.
See: https://benchling.com/help/widget
"""

from django.utils.safestring import mark_safe
from django import template
import django.utils.html as html

import rotmic.utils.genbank as genbank

register = template.Library()

benchling_script=\
"""
<div id="%(element)s"/>
  <script>
  widget = new benchling.Widget(document.getElementById('%(element)s'));
  var params = {
        "sequence": {
            "name": "%(name)s",
            "bases": "%(sequence)s",
            "circular": false,
            "annotations": [
            %(annotations)s
            ]
        },
        "options": {}
    };
  widget.load(params);
  </script>
</div>
"""

benchling_annotation=\
"""
{
   'name': "%(name)s",
   'color': "%(color)s",
   'start': %(start)i,
   'end': %(end)i,
   'strand' : %(strand)i,
},
"""

@register.simple_tag
def benchling_libs():
    """benchling javascript import statement"""
    return "<script src='https://benchling.com/static/build/api.js?v=1.0' type='text/javascript'></script>"

@register.simple_tag
def benchling(dc, element='sequence-box'):
    """display Benchling Sequence widget"""

    sequence = dc.sequence
    if not sequence:
        return mark_safe("<p>There is no sequence registered.</p>")
    
    annotations = ''
    if dc.genbank:
        p = genbank.GenbankInMemory(dc.genbank)
        for feature in p.features:
            annotations += benchling_annotation % feature + '\n'
    
    d = {'element': element,
         'name': dc.displayId,
         'sequence' : sequence,
         'annotations' : annotations }
    r = benchling_script % d

    return mark_safe(r)