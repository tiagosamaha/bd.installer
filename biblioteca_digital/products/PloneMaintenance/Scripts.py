# -*- coding: utf-8 -*-
## PloneMaintenance
## Run cheduled scripts for routine work in a Plone site, like packing the ZODB
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# Code adapted from DCWorkflow/Scripts

from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

try:
    from Products.CMFCore.CMFCorePermissions import ManagePortal
except:
    from Products.CMFCore.permissions import ManagePortal

from Products.DCWorkflow.ContainerTab import ContainerTab


class Scripts(ContainerTab):

    meta_type = 'Maintenance Scripts'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    def manage_main(self, client=None, REQUEST=None, **kw):
        '''
        '''
        kw['management_view'] = 'Scripts'
        m = Folder.manage_main.__of__(self)
        return m(self, client, REQUEST, **kw)
        
InitializeClass(Scripts)
