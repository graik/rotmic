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
"""Base Admin extensions used by many ModelAdmins"""

import datetime

class BaseAdminMixin:
    """
    Automatically save and assign house-keeping information like by whom and
    when a record was saved.
    """

    def save_model(self, request, obj, form, change):
        """Override to save user who created this record"""
        ## do if new object or if object is being recovered by reversion
        if not change or '/recover/' in request.META['HTTP_REFERER']:
            obj.registeredBy = request.user
            obj.registeredAt = datetime.datetime.now()
            
        if change and form.has_changed():
            obj.modifiedBy = request.user
            obj.modifiedAt = datetime.datetime.now()

        obj.save()


