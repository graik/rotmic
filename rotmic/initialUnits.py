"""
Pre-populate database with Unit instances that are needed for templates
and pre-defined actions.
"""
from __future__ import unicode_literals
from rotmic.models import Unit
import logging

def getcreate(name='', unitType='volume', conversion=1.0, **kwargs):
    """
    Look up Unit of given name or create a new one and save it to the DB.
    """
    try:
        r = Unit.objects.get(name=name, unitType=unitType)
    except Unit.DoesNotExist:
        r = Unit( name=name, unitType=unitType, conversion=conversion, **kwargs)
        r.save()
        logging.warning('Created missing Unit: %s.' % name )

    return r

## Volume units
l = getcreate('L', unitType='volume', conversion=1.0)
ml = getcreate('ml', unitType='volume', conversion=1e-3)
ul = getcreate("\xb5l", unitType='volume', conversion=1e-6)

## Mass units
g = getcreate('g', unitType='mass', conversion=1.0)
kg = getcreate('kg', unitType='mass', conversion=1000)
mg = getcreate('mg', unitType='mass', conversion=1e-3)
ug = getcreate('\xb5g', unitType='mass', conversion=1e-6)

## molar units
mol = getcreate('mol', unitType='number', conversion=1.0)
mmol = getcreate('mmol', unitType='number', conversion=1e-3)
umol = getcreate('\xb5mol', unitType='number', conversion=1e-6)
nmol = getcreate('nmol', unitType='number', conversion=1e-9)
items = getcreate('items', unitType='number', conversion=0.0)

## concentration units
M = getcreate('M', unitType='concentration', conversion=1.0)
mM = getcreate('mM', unitType='concentration', conversion=1e-3)
uM = getcreate('\xb5M', unitType='concentration', conversion=1e-6)
gl = getcreate('g/l', unitType='concentration', conversion=0.0)
ngul = getcreate('ng/\xb5l', unitType='concentration', conversion=0.0)