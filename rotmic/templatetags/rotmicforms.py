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

import markdown2
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag('rotmic/rotmic_formrow.html')
def formrow(*formfields, **kwargs):
    """
    Display single or multiple (grouped) form field input with help text, 
    label, mouseover etc mirroring the way Admin is doing it.
    
    Note -- Special tooltip behavior:
    If the field.help_text has more than one line ('\n'), only the first line
    is displayed as small help text and the remaining multiline string is used
    as a tooltip (mouseover).
    
    formfield - formfield instance (from django.forms.Form)
    tooltip   - bool, copy help text to tooltip (False) and display both, 
                ignored if help_text has multiple lines.
    ignoreRequired - bool, do not set required style (bold) even if field.requried
    """
    tooltip = kwargs.get('tooltip', False)
    ignoreRequired = kwargs.get('ignoreRequired', False)
    
    for field in formfields:
        
        help = field.help_text
        mouseover = help if tooltip else None
    
        if help.count('\n') > 0:
            pos = help.index('\n')
            field.help_text = help[:pos]
            if len(help) > pos+1:
                mouseover = help[pos+1:]
    
        required = False if ignoreRequired else field.field.required
          
        field.mouseover = mouseover
        field.required = required
        
    return {'fields':formfields}