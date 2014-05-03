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
Django template tags for built-in D3 sequence display widget

Use:
   {% load seqdisplay %}
   ...
   {% block extrastyles %}{{ block.super }}
       {% seqdisplay_css %}
   {% endblock %}
   ...
   {% block extrahead %}{{ block.super }}
       {% seqdisplay_libs %}
   {% endblock %}
   ...
   <div id='seqdisplaybox'></div>
   {% seqdisplay o 'seqdisplaybox' %}

Where 'o' is a Dna/ProteinComponent object from the template context.
"""

from django.utils.safestring import mark_safe
from django import template
import django.utils.html as html
import django.contrib.staticfiles.templatetags.staticfiles as ST

import rotmic.utils.genbank as genbank

register = template.Library()

seqdisplay_script=\
"""
  <script>
  var sequence = '%(sequence)s';
  var features = [
  %(annotations)s
  ]

  seqdisplay.init('%(element)s');
  seqdisplay.load(sequence, features);
  </script>
"""

seq_warning=\
"""
<div>
    <p>
       <b>Warning:</b> The registered sequence does not match the registered genbank record.
       Displaying the sequence extracted from the genbank record.
    </p>
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
def seqdisplay_libs():
    """benchling javascript import statement"""
    f = ST.static('d3sequence.js')
    r = "<script src='http://d3js.org/d3.v3.min.js' charset='utf-8'></script>\n"
    r += "<script src='%s' type='text/javascript'></script>" % f
    return r

@register.simple_tag
def seqdisplay_css():
    f = ST.static('d3sequence.css')
    return "<link rel=stylesheet' type='text/css' href='%s'/>" % f

@register.simple_tag
def seqdisplay(dc, element='seqdisplay'):
    """display D3 Sequence widget"""

    sequence = dc.sequence
    if not sequence and not dc.genbank:
        return mark_safe("<p>There is no sequence registered. Upload a genbank file to show annotations.</p>")
    
    annotations = ''
    errors = ''
    if dc.genbank:
        p = genbank.GenbankInMemory(dc.genbank)
        for feature in p.features:
            annotations += benchling_annotation % feature

        if sequence and sequence != p.sequence:
            errors += seq_warning
            sequence = p.sequence
    
    d = {'element': element,
         'name': dc.displayId,
         'sequence' : sequence,
         'annotations' : annotations }
    r = seqdisplay_script % d + errors

    return mark_safe(r)