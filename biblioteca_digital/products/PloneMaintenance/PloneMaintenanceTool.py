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

"""PloneMaintenanceTool main class"""

from string import find
from Products.CMFCore.utils import UniqueObject, _getAuthenticatedUser, _checkPermission
from Products.CMFCore.utils import getToolByName, _dtmldir
from OFS.Folder import Folder
from Globals import InitializeClass, DTMLFile, MessageDialog, ImageFile, \
     PersistentMapping
from Acquisition import aq_base
from AccessControl.User import nobody
from AccessControl import ClassSecurityInfo
try:
    from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
except:
    from Products.CMFCore.permissions import ViewManagementScreens
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from DateTime import DateTime

from global_symbols import *

import sys

def addPloneMaintenanceTool(self,REQUEST={}):
    """
    Factory method for the PloneMaintenance Tool
    """
    id = 'portal_maintenance'
    pat = PloneMaintenanceTool()
    self._setObject(id, pat, set_owner=0)
    getattr(self, id)._post_init()
    if REQUEST:
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_main')

def getNoSecDate(date):
    return DateTime(date.Date() + ' ' + date.TimeMinutes())

class PloneMaintenanceTool(UniqueObject, Folder, ActionProviderBase):
    """
    PloneMaintenance Tool
    """

    id = 'portal_maintenance'
    meta_type = 'PloneMaintenance Tool'
    _actions = []
    security = ClassSecurityInfo()

    scripts = None
    tasks = None

    manage_options = (
        ( {'label' : 'Overview',
           'action' : 'manage_overview'},
          {'label': 'Tasks',
           'action': 'tasks/manage_main'},
          {'label': 'Scripts',
           'action': 'scripts/manage_main'},
        ) +
         ActionProviderBase.manage_options +
         Folder.manage_options
        )

    security.declareProtected(ViewManagementScreens, 'manage_overview')
    manage_overview = DTMLFile('dtml/explainMaintenanceTool', globals())

    def __init__(self):
        # Properties to be edited by site manager
        #self.safeEditProperty(self, 'is_Active', 0, data_type='int')

        from Scripts import Scripts
        self._addObject(Scripts('scripts'))
        from Tasks import Tasks
        self._addObject(Tasks('tasks'))
        pass

    def _addObject(self, ob):
        id = ob.getId()
        setattr(self, id, ob)
        self._objects = self._objects + (
            {'id': id, 'meta_type': ob.meta_type},)

    def _post_init(self):
        """
        _post_init(self) => called from manage_add method, acquired within ZODB (__init__ is not)
        """
        #self._updateProperty('site_models', self.getAvailableModels())
        pass

    def isRunning(self,):
        """
        Return whether the tool is currently running
        """
        return getattr(self, "_v_running", 0)

    security.declarePublic('runTasks')
    def runTasks(self):
        """ Run the tasks """
        if self.isRunning():
            message = "Can't run Tasks. Maintenance Tool is still running."
            Log(LOG_NOTICE, message)
            return message
        else:
            Log(LOG_DEBUG, "Running Tasks")
            self._v_running = 1
            run = 0
            failed = 0
            number_of_tasks = len(self.tasks.items())
            for id, task in self.tasks.items():
                date=getNoSecDate(DateTime())
                if task.isPending(date): # If the task is pending, it has to be executed
                    run += 1
                    if task.runTask(date):
                        pass # Everything went ok
                    else:
                        failed += 1
            self._v_running = 0

            message = ""

            if number_of_tasks == 0:
                message += "No tasks available. Add them to the portal_maintenance tool along with the scripts to run."
            elif number_of_tasks == 1:
                message += "One Task available."
            else:
                message += "%d Tasks available." % number_of_tasks

            if run == 0:
                message += " No scripts were run."
            elif run == 1:
                message = " One script was run."
            else:
                message = " Finished running %d scripts." % run

            if failed == 0:
                message += " No scripts failed."
            elif run == 1:
                message = " One script failed."
            else:
                message = " %d scripts failed." % run

            Log(LOG_DEBUG, message )
        return message

InitializeClass(PloneMaintenanceTool)
