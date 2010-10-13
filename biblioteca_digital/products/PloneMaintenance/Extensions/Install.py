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
"""
Installer utility
"""
__version__ = "$Revision: 26105 $"
# $Source$
# $Id: Install.py 26105 2006-07-13 14:12:40Z clebeaupin $
__docformat__ = 'restructuredtext'

from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod

from Products.CMFCore.utils import getToolByName

from Products.PloneMaintenance import install_globals, MaintenanceTask
from Products.PloneMaintenance.global_symbols import *
from Products.PloneMaintenance.Installation import Installation
from Products.PloneMaintenance.PloneMaintenanceTool import addPloneMaintenanceTool


fti_list = (
    MaintenanceTask.factory_type_information,
    )

types_list = (
    "MaintenanceTask",
    )

skin_name = "PloneMaintenance"

product_name = "PloneMaintenance"

def setupTools(self):
    tool_meta_type = 'PloneMaintenance Tool'
    id = "portal_maintenance"

    if not self.objectIds(spec=tool_meta_type):
        addPloneMaintenanceTool(self)
    else:
        pass

def updateTaskProperties(self):
    """Check task properties and add it if they don't exist"""
    
    mtool = getToolByName(self, 'portal_maintenance')
    for id, task in mtool.tasks.items():
        # Check notified emails property
        property_id = 'notified_emails'
        if not task.hasProperty(property_id):
            task._setProperty(property_id, [], 'lines')
            
        # Fix id of tasks
        if not task.getId():
            task.id = id

def install(self, reinstall=0):
    installation=Installation(self)
    out = installation.out

    installation.setupTypesandSkins(fti_list, skin_name, install_globals, [])

    # Disallow adding MaintenanceTask
    ttool = getToolByName(self, 'portal_types')
    typeinfo = getattr(ttool, 'MaintenanceTask')
    try:
        typeinfo.manage_changeProperties({"global_allow":0})
    except:
        typeinfo.manage_changeProperties(global_allow=0) # Doesn't work with Plone 2.0.5
   
    if not reinstall:
        setupTools(self)

        mainttool = getToolByName(self, 'portal_maintenance')
        scriptsholder = mainttool.scripts

        # Plone Catalog update script
        manage_addExternalMethod(scriptsholder,'updateCatalog',
            'Update the portal catalog',
            PROJECTNAME+'.MaintenanceToolbox',
            'updateCatalog')

        # Plone Catalogs rebuilds script
        manage_addExternalMethod(scriptsholder,'rebuildCatalogs',
            'PloneArticle-aware Rebuild of all Catalogs',
            PROJECTNAME+'.MaintenanceToolbox',
            'rebuildCatalogs')

        # Pack DB script
        manage_addExternalMethod(scriptsholder,'packDB',
            'Pack the main DB or any specified one',
            PROJECTNAME+'.MaintenanceToolbox',
            'packDB')

        # Archive expired content script
        manage_addExternalMethod(scriptsholder,'archiveExpiredContent',
            'Archive expired content script',
            PROJECTNAME+'.MaintenanceToolbox',
            'archiveExpiredContent')
    else:
        updateTaskProperties(self)
            
    return installation.report()
