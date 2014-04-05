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
import re

from django.db import models
from django.db.models import Q
import django.utils.html as html

from .usermixin import UserMixin, ReadonlyUrlMixin

import rotmic.templatetags.rotmicfilters as F

class Project(UserMixin, ReadonlyUrlMixin):
    """
    A project connecting users / groups to constructs
    """

    name = models.CharField('Project Name', max_length=200, unique=True, 
                            help_text='Unique name')

    description = models.TextField('Description', blank=True,
                help_text='You can format your text and include links. See: <a href="http://daringfireball.net/projects/markdown/basics">Markdown Quick Reference</a>')


    def __unicode__(self):
        return unicode(self.name)

    def descriptionText(self):
        """remove some formatting characters from text"""
        r = re.sub('--','', self.description)
        r = re.sub('=','', r)
        r = re.sub('__','', r)
        return r
    descriptionText.short_description = 'description'

    def showDescription(self):
        """
        @return: str; truncated description with full description mouse-over
        """
        if not self.description: 
            return u''
        if len(self.description) < 40:
            return unicode(self.description)
        r = unicode(self.description[:38])
        r = html.mark_safe('<a title="%s">%s</a>' \
                           % (self.description, F.truncate(self.descriptionText(), 40)))
        return r
    showDescription.allow_tags = True
    showDescription.short_description = 'Description'

    def showVerbose(self):
        url = self.get_absolute_url()
        title = 'Project\n%s' % (self.name)
        return html.mark_safe('<a href="%s" title="%s">%s</a>' \
                              % (url, title, self.name) )
    showVerbose.allow_tags = True
    showVerbose.short_description = 'Project'

    class Meta:
        app_label = 'rotmic'
        ordering = ('name',)
        verbose_name = 'Project'

