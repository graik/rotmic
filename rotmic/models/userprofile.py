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
"""Add user-specific settings to default User model"""

from django.contrib.auth.models import User
import django.db.models as models
from django.db.models.signals import post_save

def userInitials(request):
    user = request.user
    if user.first_name and user.last_name:
        return user.first_name[0] + user.last_name[0]
    return user.name[:2]


class UserProfile(models.Model):
    """User profile to attach extra user settings to the built-in User model"""
    
    user = models.OneToOneField(User, related_name='profile')
    
    prefix = models.CharField('default Prefix', max_length=5,
                              default='id',
                              help_text='default ID prefix')
    
    dcPrefix = models.CharField('DNA Prefix', max_length=5,
                                help_text='default ID prefix for DNA constructs',
                                blank=True)
    
    ccPrefix = models.CharField('Cell Prefix', max_length=5,
                                help_text='default ID prefix for Cells',
                                blank=True)
    
    ocPrefix = models.CharField('Oligo Prefix', max_length=5,
                                help_text='default ID prefix for Oligos',
                                blank=True)
    
    chPrefix = models.CharField('Chemical Prefix', max_length=5,
                                help_text='default ID prefix for Chemicals',
                                blank=True)
    
    pcPrefix = models.CharField('Protein Prefix', max_length=5,
                                help_text='default ID prefix for Proteins',
                                blank=True)

    def __unicode__(self):
        return unicode(self.user)
    
    class Meta:
        app_label = 'rotmic'
        ordering = ('user',)

def user_initials(user):
    try:
        if user.first_name and user.last_name:
            return (user.first_name[0] + user.last_name[0]).lower()
        return user.username[:2]
    except:
        return 'id'

def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        prefix = user_initials(user)  ## first and last name is not yet set at this point
        profile = UserProfile(user=user, prefix=prefix)
        profile.save()

post_save.connect(create_profile, sender=User)

