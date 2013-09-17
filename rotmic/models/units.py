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
from django.db import models

class Unit(models.Model):
    """
    Unit for amount, concentration, volume
    """

    UNIT_TYPE = (('mass','mass'), 
                 ('volume','volume'), 
                 ('concentration','concentration'),
                 ('number','number'),
                 ('other','other'))

    name = models.CharField(max_length=10, unique=True)

    unitType = models.CharField(max_length=25, choices=UNIT_TYPE,
                                verbose_name='Type of Unit')

    conversion = models.FloatField('Conversion Factor', blank=True, null=True,
                                   help_text='Factor for conversion to SI unit')

    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = 'rotmic'    
        ordering = ['unitType', 'conversion', 'name']
        

