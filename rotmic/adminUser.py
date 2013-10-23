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
"""Extension of default User admin"""

from django.contrib import admin

from rotmic.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    
    readonly_fields = ('user',)

    fieldsets = (
        (None, {'fields':('user',),
                'description':'Adjust user-specific settings for:',
                }
         ),
        
        ('ID suggestion', 
            {'fields': ('prefix', ('dcPrefix', 'ccPrefix', 'ocPrefix')),
             'description': 'Adjust prefix for autogeneration of DNA, Cell and Oligo IDs. '\
                          + '(For DNA, it will be further modified according to the selected category.)'
            }
        ),
    )
    
    ordering = ('user',)
    
    list_display = ('user', 'prefix', 'dcPrefix', 'ccPrefix', 'ocPrefix')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    
    actions = None ## disable delete action
    
    def has_delete_permission(self, request, obj=None):
        """Disable deletion of profile (only deleted with user)"""
        return False    
    
    
admin.site.register(UserProfile, UserProfileAdmin)
