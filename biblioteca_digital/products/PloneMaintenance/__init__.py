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

"""PloneMaintenance"""
import AccessControl.Permissions
import MaintenanceTask
import PloneMaintenanceTool

from Products.CMFCore import utils
import Tasks, Scripts


from global_symbols import *

from AccessControl.Permissions import *

from Products.CMFCore.DirectoryView import registerDirectory
try:
    from Products.CMFCore.CMFCorePermissions import ManagePortal
except:
    from Products.CMFCore.permissions import ManagePortal

registerDirectory('skins', globals())
registerDirectory('skins/PloneMaintenance', globals())

install_globals = globals()          # Used only in the Extensions/Install.py script

# Classes & constructors declaration
contentClasses = (MaintenanceTask.MaintenanceTask, )
contentConstructors = (MaintenanceTask.addMaintenanceTask, )

# Initialization method
def initialize(context):

    utils.ContentInit(
        'MaintenanceTask',
        content_types = contentClasses,
        permission = ManagePortal,
        extra_constructors = contentConstructors,
        fti = (MaintenanceTask.factory_type_information,),
        ).initialize(context)

    context.registerClass(
        PloneMaintenanceTool.PloneMaintenanceTool,
        meta_type="PloneMaintenance Tool",
        constructors=(PloneMaintenanceTool.addPloneMaintenanceTool,),
        icon = 'tool.gif')

    utils.registerIcon(Tasks.Tasks,
                 'images/task.gif', globals())

    utils.registerIcon(Scripts.Scripts,
                 'images/script.gif', globals())

