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

#
# Runs all tests in the current directory
#
# Execute like:
#   python runalltests.py
#
# Alternatively use the testrunner: 
#   python /path/to/Zope/utilities/testrunner.py -qa
#
"""
"""

__author__ = 'Maik Röder <maik.roeder@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import time

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.setup import PLONE21, PLONE25

# We need Five (zope 2.8) and require kupu under plone 2.1
if PLONE21:
    ZopeTestCase.installProduct('Five')
    ZopeTestCase.installProduct('kupu')

ZopeTestCase.installProduct('PloneMaintenance')
PloneTestCase.setupPloneSite(products=["PloneMaintenance"])


from Products.CMFPlone.utils import transaction

#ZopeTestCase.installProduct('PloneMaintenance')

class PloneMaintenanceTestCase(PloneTestCase.PloneTestCase):
    """PloneMaintenance test"""

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
    
    
    def afterSetUp(self):
        # Remove Tasks
        ids=self.portal.portal_maintenance.tasks.objectIds()
        self.portal.portal_maintenance.tasks.manage_delObjects(ids)
        
    def beforeTearDown(self):
        self.logout()


