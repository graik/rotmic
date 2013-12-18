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
import datetime

import django.forms as forms
from django.core.exceptions import ValidationError
import django.contrib.messages as messages

import selectLookups as L
import selectable.forms as sforms

import rotmic.models as M

import rotmic.initialTypes as T
import rotmic.initialUnits as U
import rotmic.utils.ids as ids


def getSampleWidgets( extra={} ):
    """widgets shared between different types of Sample forms."""
    r = {
        'container' : sforms.AutoComboboxSelectWidget(lookup_class=L.SampleContainerLookup,
                                                     allow_new=False),

        'displayId' : forms.TextInput(attrs={'size':5}),
        
        'concentration' : forms.TextInput(attrs={'size':5}),

        'amount' : forms.TextInput(attrs={'size':5}),

        'aliquotNr' : forms.TextInput(attrs={'size':2}),
        'description': forms.Textarea(attrs={'cols': 100, 'rows': 5,
                                         'style':'font-family:monospace'}) }
    r.update( extra )
    return r

class SampleForm(forms.ModelForm):
    """Customized Form for Sample add / change. 
    To be overridden rather than used directly."""
    
    def __init__(self, *args, **kwargs):
        """Rescue request object from kwargs pushed in from SampleAdmin"""
        self.request = kwargs.pop('request', None)
        super(SampleForm, self).__init__(*args, **kwargs)

    def clean_displayId(self):
        r = self.cleaned_data['displayId']
        r = r.strip()
        
        letter, number = ids.splitSampleId( r )
        
        if number is None:
            raise ValidationError('Valid IDs must be of form "A01" or "01"')
        
        letter = letter.upper()
        number = '%02i' % number
        return letter + number
    
    
    def clean(self):
        """
        Verify that units are given if concentration and/or amount is given.
        """
        data = super(SampleForm, self).clean()
        conc = data.get('concentration', None)
        concUnit = data.get('concentrationUnit', None)
        amount = data.get('amount', None)
        amountUnit = data.get('amountUnit', None)
    
        ## reset units to None if no concentration and / or amount is given
        if not conc and concUnit:
            data['concentrationUnit'] = None
        if not amount and amountUnit:
            data['amountUnit'] = None
        
        ## validate that units are given if conc. and / or amount is given
        if conc and not concUnit:
            msg = u'please specify concentration unit'
            self._errors['concentrationUnit'] = self.error_class([msg])
    
        if amount and not amountUnit:
            msg = u'please specify amount unit'
            self._errors['amountUnit'] = self.error_class([msg])
        
        return data

    class Meta:
        model = M.Sample
        widgets = getSampleWidgets()
            


class DnaSampleForm( SampleForm ):
    """Customized Form for DnaSample add / change"""
    
    ## modify initial (default) value
    concentrationUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=L.ConcentrationUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=L.ConcentrationUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.ngul)
    
    ## restrict available choices to volume units only
    amountUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=L.VolumeAmountUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=L.VolumeAmountUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.ul)

    class Meta:
        model = M.DnaSample
        widgets = getSampleWidgets( \
            {'dna': sforms.AutoComboboxSelectWidget(lookup_class=L.SampleDnaLookup,
                                                    allow_new=False,
                                                    attrs={'size':35}),
             })


class CellSampleForm( SampleForm ):
    """Customized Form for CellSample add / change"""
    
    cellCategory = forms.ModelChoiceField(label='In Species',
                            queryset=M.CellComponentType.objects.filter(subTypeOf=None),
                            required=False, 
                            empty_label=None,
                            initial=T.ccEcoli)
    
    cellType = forms.ModelChoiceField(label='Strain',
                            queryset=M.CellComponentType.objects.exclude(subTypeOf=None),
                            required=False,
                            empty_label=None,
                            initial=T.ccMach1)
    
    plasmid = sforms.AutoCompleteSelectField(label='Plasmid',
                            lookup_class=L.PlasmidLookup,
                            required=False,
                            help_text='Start typing name or ID...',
                            widget=sforms.AutoCompleteSelectWidget(lookup_class=L.PlasmidLookup,
                                                        allow_new=False,
                                                        attrs={'size':35}),)

    
    ## restrict available choices to volume units only
    amountUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=L.VolumeAmountUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=L.VolumeAmountUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.ul)

    def __init__(self, *args, **kwargs):
        super(CellSampleForm, self).__init__(*args, **kwargs)

        ## keep constraint on DB level but allow user to specify via plasmid+type
        self.fields['cell'].required = False

        o = kwargs.get('instance', None)
        if o:
            self.fields['cellCategory'].initial = o.cell.componentType.category()
            self.fields['cellType'].initial = o.cell.componentType
            self.fields['plasmid'].initial = o.cell.plasmid

    def clean(self):
        """
        Verify that cell or plasmid + strain are given, create new cell if needed.
        """
        super(CellSampleForm, self).clean()
        data = self.cleaned_data
        cell = data.get('cell', None)
        plasmid = data.get('plasmid', None)
        ctype = data.get('cellType', None)
        
        if not cell and not (plasmid and ctype):
            msg = u'Please specify either an existing cell or a plasmid and strain.'
            self._errors['cell'] = self.error_class([msg])
            try: 
                del data['cell'] ## needed to really stop form saving
            except: 
                pass
            
        elif plasmid and cell:
            if plasmid != cell.plasmid:
                msg = u'Given plasmid does not match selected cell record. Remove one or the other.'
                self._errors['plasmid'] = self.error_class([msg])
                del data['plasmid']
            if ctype != cell.componentType:
                msg = u'Given strain does not match selected cell record. Clear either plasmid or cell selection.'
                self._errors['cellType'] = self.error_class([msg])
                del data['cellType']
            
        if (not cell) and plasmid:
            
            existing = M.CellComponent.objects.filter(plasmid=plasmid,
                                                    componentType=ctype)
            if existing.count():
                data['cell'] = existing.all()[0]
                messages.success(self.request, 
                                 'Attached existing cell record %s (%s) to sample.'\
                                 % (data['cell'].displayId, data['cell'].name))
            
            else:
                newcell = M.CellComponent(componentType=ctype,
                                        plasmid=plasmid,
                                        displayId=ids.suggestCellId(self.request.user.id),
                                        registeredBy = self.request.user,
                                        registeredAt = datetime.datetime.now(),
                                        name = plasmid.name + '@' + ctype.name,
                                        )
                newcell.save()
                data['cell'] = newcell
                messages.success(self.request,
                                 'Created new cell record %s (%s)' %\
                                 (newcell.displayId, newcell.name))

        return data
    
    
    class Meta:
        model = M.CellSample
        widgets = getSampleWidgets( \
            {'cell': sforms.AutoComboboxSelectWidget(lookup_class=L.SampleCellLookup,
                                                    allow_new=False,
                                                    attrs={'size':35}),
             })

        
class OligoSampleForm( SampleForm ):
    """Customized Form for DnaSample add / change"""
    
    ## modify initial (default) value
    concentrationUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=L.ConcentrationUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=L.ConcentrationUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.uM)
    
    ## restrict available choices to volume units only
    amountUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=L.VolumeAmountUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=L.VolumeAmountUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.ul)

    class Meta:
        model = M.OligoSample
        widgets = getSampleWidgets( \
            {'oligo': sforms.AutoComboboxSelectWidget(lookup_class=L.OligoLookup,
                                                      allow_new=False,
                                                      attrs={'size':35}),
             })

class ChemicalSampleForm( SampleForm ):
    """Customized Form for ChemicalSample add / change"""
    
    ## modify initial (default) value
    concentrationUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=L.ConcentrationUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=L.ConcentrationUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.M)
    
    ## restrict available choices to volume units only
    amountUnit = sforms.AutoCompleteSelectField(
        label='... unit',
        required=False,
        lookup_class=L.VolumeAmountUnitLookup,
        allow_new=False,
        widget=sforms.AutoComboboxSelectWidget(lookup_class=L.AmountUnitLookup,
                                               allow_new=False,attrs={'size':5}),
        initial=U.g)

    class Meta:
        model = M.ChemicalSample
        widgets = getSampleWidgets( \
            {'chemical': sforms.AutoComboboxSelectWidget(lookup_class=L.ChemicalLookup,
                                                      allow_new=False,
                                                      attrs={'size':35}),
             })

class SampleProvenanceForm( forms.ModelForm ):
    """minimal form used inline for sample History records"""
    
    def clean_sourceSample(self):
        r = self.cleaned_data['sourceSample']
        t = self.cleaned_data['provenanceType']

        if t and t.requiresSource and not r:
            raise ValidationError('%s requires a source sample.' % unicode(t))
        
        return r
        
    
    class Meta:
        widgets = {'sourceSample': sforms.AutoComboboxSelectWidget(lookup_class=L.ProvenanceSampleLookup,
                                                                   allow_new=False,
                                                                   attrs={'size':20})
                   }