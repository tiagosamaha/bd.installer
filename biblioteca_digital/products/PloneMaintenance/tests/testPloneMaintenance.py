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

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# use recent version (0.6+) of PloneTestCase from CVS:
from Products.PloneTestCase import PloneTestCase

from Products.PloneMaintenance.MaintenanceTask import addMaintenanceTask
from Products.PloneMaintenance.global_symbols import *
from Products.PloneMaintenance.PloneMaintenanceTool import getNoSecDate
from Products.PloneMaintenance.tests import plonemaintenancetestcase

PloneTestCase.installProduct('PloneMaintenance')
PloneTestCase.setupPloneSite()
from Testing import ZopeTestCase # side effect import. leave it here.

from AccessControl import getSecurityManager

from DateTime import DateTime

from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod

# Set log options if Log module is available
# This is done to set LOG_PROCESSORs to file logs instead of Zope logs
try:
    import Log

    Log.LOG_LEVEL = Log.LOG_DEBUG

    Log.LOG_PROCESSOR = {
        Log.LOG_NONE: Log.logFile,
        Log.LOG_CRITICAL: Log.logFile,
        Log.LOG_ERROR: Log.logFile,
        Log.LOG_WARNING: Log.logFile,
        Log.LOG_NOTICE: Log.logFile,
        Log.LOG_DEBUG: Log.logFile,
        }

    from Log import *
    Log(LOG_NOTICE, "Starting %s at %d debug level" % (os.path.dirname(__file__), LOG_LEVEL, ))

except:
    print "Log module not available"
    LOG_DEBUG = None
    LOG_NOTICE = None
    LOG_WARNING = None
    LOG_ERROR = None
    LOG_CRITICAL = None
    def Log(*args, **kw):
        pass
    raise

class TestPloneMaintenance(plonemaintenancetestcase.PloneMaintenanceTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.qi = self.portal.portal_quickinstaller
        self.qi.installProduct('PloneMaintenance')
        self.securityManager = getSecurityManager()

    def login(self, userid=None):
        if userid:
            PloneTestCase.PloneTestCase.login(self, userid)
            pm = getToolByName(self.portal, 'portal_membership')
            self.portal.REQUEST.set('_portaluser', pm.getMemberById(userid))
        else:
            PloneTestCase.PloneTestCase.login(self)

    def test_01_check_defaults(self,):
        """
        """
        # Set a valid model
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        self.failUnless(task.getProperty('scheduled_month')=='*')
        #self.failUnless(task.getProperty('scheduled_day_of_week')=='*')
        self.failUnless(task.getProperty('scheduled_day_of_month')=='*')
        self.failUnless(task.getProperty('scheduled_hour')=='*')
        self.failUnless(task.getProperty('scheduled_minute')=='*')
        self.failUnless(task.getProperty('script_name')=='')
        date = getNoSecDate(DateTime())
        self.failUnless(task.isPending(date)==1) # By default always run.
        current_date=getNoSecDate(DateTime())
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(next_scheduled >= date, str(next_scheduled) + " not >= " + str(date))


    def test_02_isPending(self,):
        """
        """
        # Set a valid model
        current_date=getNoSecDate(DateTime())
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)

        # Should be run this month
        task.setScheduled_month(str(current_date.month()))

        next_scheduled = task.getNextScheduledExecutionTime(current_date)

        self.failUnless( next_scheduled >= current_date, str(next_scheduled) + " not >= " + str(current_date))

    def test_03_execution(self,):
        """
        """
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        date = getNoSecDate(DateTime())
        self.failUnless(task.runTask(date)==0) # Didn't run as script is empty

    def test_04_beforeIntervall(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/05/16 15:40')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_hour('15')
        task.setScheduled_minute('20')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2004/05/17 15:20') == next_scheduled, str(DateTime('2004/05/17 15:20')) + ' != ' + str(next_scheduled))


    def test_05_beforeIntervall(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/05/01 00:40')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('5')
        task.setScheduled_minute('10')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2005/05/01 00:10')==next_scheduled)

    def test_06_beforeIntervall(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/05/01 00:40')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2004/05/01 00:40')==next_scheduled)

    def test_07_beforeIntervall(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/05/17 10:16')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('5')
        task.setScheduled_day_of_month('17')
        task.setScheduled_hour('10')
        task.setScheduled_minute('15')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2005/05/17 10:15')==next_scheduled)

    def test_08_nextYear(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/05/17 10:16')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('4')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('*')
        task.setScheduled_minute('*')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2005/04/01 00:00') == next_scheduled)

    def test_09_nextMonth(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/05/17 10:16')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('4')
        task.setScheduled_day_of_month('1')
        task.setScheduled_hour('*')
        task.setScheduled_minute('*')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2005/04/01 00:00') == next_scheduled)

    def test_10_month_end(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/02/29 10:16')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('2')
        task.setScheduled_day_of_month('28')
        task.setScheduled_hour('*')
        task.setScheduled_minute('*')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2005/28/02 00:00') == next_scheduled, str(DateTime('2005/28/02 00:00')) + ' != ' + str(next_scheduled))

    def test_11_minute(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('*')
        task.setScheduled_minute('47')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/04/25 09:47')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_12_hour(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('10')
        task.setScheduled_minute('*')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2004/04/25 10:00') == next_scheduled)

    def test_13_day(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('27')
        task.setScheduled_hour('*')
        task.setScheduled_minute('*')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2004/04/27 00:00') == next_scheduled)

    def test_14_month(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('12')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('*')
        task.setScheduled_minute('*')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2004/12/01 00:00') == next_scheduled, str(DateTime('2004/12/01 00:00'))+' != ' + str(next_scheduled))

    def test_15_day_minute(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('26')
        task.setScheduled_hour('*')
        task.setScheduled_minute('12')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/04/26 00:12')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_16_day_hour(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_day_of_month('26')
        task.setScheduled_hour('11')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/04/26 11:00')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_17_day_hour_minute(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_day_of_month('26')
        task.setScheduled_hour('11')
        task.setScheduled_minute('11')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/04/26 11:11')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_18_month_hour(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('7')
        task.setScheduled_hour('11')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/07/01 11:00')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_19_month_hour_minute(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('7')
        task.setScheduled_hour('11')
        task.setScheduled_minute('11')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/07/01 11:11')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_20_month_day_minute(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('7')
        task.setScheduled_day_of_month('11')
        task.setScheduled_hour('*')
        task.setScheduled_minute('11')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/07/11 00:11')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))


    def test_21_month_day_hour(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('7')
        task.setScheduled_day_of_month('11')
        task.setScheduled_hour('11')
        task.setScheduled_minute('*')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/07/11 11:00')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_22_minute(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:47')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('*')
        task.setScheduled_minute('47')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/04/25 09:47')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_23_minute(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:49')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('*')
        task.setScheduled_minute('47')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/04/25 10:47')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_24_minute(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 23:49')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('*')
        task.setScheduled_minute('47')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/04/26 00:47')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_25_minute(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 23:49')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('*')
        task.setScheduled_minute('47')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/04/26 00:47')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_26_minute_day(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 23:49')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('7')
        task.setScheduled_hour('*')
        task.setScheduled_minute('47')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        correct_date = DateTime('2004/05/07 00:47')
        self.failUnless(correct_date == next_scheduled, str(correct_date) +' != ' + str(next_scheduled))

    def test_27_hour(self,):
        """
        """
        last_update=DateTime('2006/05/05 16:05')
        current_date=DateTime('2006/05/11 16:38')
        correct_next_scheduled = DateTime('2006/05/12')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.last_execution_date = last_update
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('0')
        task.setScheduled_minute('*')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)

        self.failUnless(task.isPending(current_date))

        self.failUnless(correct_next_scheduled == next_scheduled, str(correct_next_scheduled) +' != ' + str(next_scheduled))

    def test_28_setting_month_differently(self,):
        """
        """
        last_update=DateTime('2006/05/05 16:05')
        current_date=DateTime('2006/05/11 16:38')
        correct_next_scheduled = DateTime('2006/05/12')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('1')
        self.failUnless(task.scheduled_month=='1')
        task.setScheduled_month(1)
        self.failUnless(task.scheduled_month=='1')
        try:
            task.setScheduled_month(120)
        except:
            pass
        self.failUnless(task.scheduled_month=='1')
        try:
            task.setScheduled_month('120')
        except:
            pass
        self.failUnless(task.scheduled_month=='1')

    def test_29_setting_day_of_month_differently(self,):
        """
        """
        last_update=DateTime('2006/05/05 16:05')
        current_date=DateTime('2006/05/11 16:38')
        correct_next_scheduled = DateTime('2006/05/12')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_day_of_month('1')
        self.failUnless(task.scheduled_day_of_month=='1')
        task.setScheduled_day_of_month(1)
        self.failUnless(task.scheduled_day_of_month=='1')
        try:
            task.setScheduled_day_of_month(120)
        except:
            pass
        self.failUnless(task.scheduled_day_of_month=='1')
        try:
            task.setScheduled_day_of_month('120')
        except:
            pass
        self.failUnless(task.scheduled_day_of_month=='1')

    def test_30_setting_hour_differently(self,):
        """
        """
        last_update=DateTime('2006/05/05 16:05')
        current_date=DateTime('2006/05/11 16:38')
        correct_next_scheduled = DateTime('2006/05/12')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_hour('1')
        self.failUnless(task.scheduled_hour=='1')
        task.setScheduled_hour(1)
        self.failUnless(task.scheduled_hour=='1')
        try:
            task.setScheduled_hour(120)
        except:
            pass
        self.failUnless(task.scheduled_hour=='1')
        try:
            task.setScheduled_hour('120')
        except:
            pass
        self.failUnless(task.scheduled_hour=='1')

    def test_31_setting_minute_differently(self,):
        """
        """
        last_update=DateTime('2006/05/05 16:05')
        current_date=DateTime('2006/05/11 16:38')
        correct_next_scheduled = DateTime('2006/05/12')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_minute('1')
        self.failUnless(task.scheduled_minute=='1')
        task.setScheduled_minute(1)
        self.failUnless(task.scheduled_minute=='1')
        try:
            task.setScheduled_minute(120)
        except:
            pass
        self.failUnless(task.scheduled_minute=='1')
        try:
            task.setScheduled_minute('120')
        except:
            pass
        self.failUnless(task.scheduled_minute=='1')

    def test_32_hour(self,):
        """
        """
        last_update=DateTime('2006/05/12 16:16')
        current_date=DateTime('2006/05/12 16:17')
        correct_next_scheduled = DateTime('2006/05/13')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.last_execution_date = last_update
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('0')
        task.setScheduled_minute('*')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failIf(task.isPending(current_date))
        self.failUnless(correct_next_scheduled == next_scheduled, str(correct_next_scheduled) +' != ' + str(next_scheduled))

    def test_33_executiondate_when_script_broken(self,):
        """
        """
        scriptsholder = self.portal.portal_maintenance.scripts
        # Plone Catalog update script
        manage_addExternalMethod(scriptsholder,'brokenScript',
            'Broken Script',
            PROJECTNAME+'.MaintenanceToolbox',
            'brokenScript')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScript_name('brokenScript')
        current_date=DateTime('2006/05/12 16:17')
        self.failUnless(task.isPending(current_date))
        last_execution_date = task.last_execution_date
        self.portal.portal_maintenance.runTasks()
        task.runTask()
        self.failUnless(task.last_execution_date!=last_execution_date)

    def test_34_executiondate_when_script_working(self,):
        """
        """
        scriptsholder = self.portal.portal_maintenance.scripts
        # Plone Catalog update script
        manage_addExternalMethod(scriptsholder,'workingScript',
            'Working Script',
            PROJECTNAME+'.MaintenanceToolbox',
            'workingScript')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScript_name('workingScript')
        current_date=DateTime('2006/05/12 16:17')
        self.failUnless(task.isPending(current_date))
        last_execution_date = task.last_execution_date
        self.portal.portal_maintenance.runTasks()
        task.runTask()
        self.failUnless(task.last_execution_date!=last_execution_date)


    def test_35_test_nextExectutionTime_with_invalid_date(self,):
        """
        """
        # Set a valid model
        current_date=DateTime('2004/04/25 09:45')
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('11')
        task.setScheduled_day_of_month('31')
        task.setScheduled_hour('*')
        task.setScheduled_minute('*')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2500/12/31 00:00') == next_scheduled)


    def test_36_month_end_2(self,):
        """Tests 28,29,30,31th of the month
        """
        # Set a valid model
        content_id = "task1"
        addMaintenanceTask(self.portal, content_id, title = 'Task 1')
        task=getattr(self.portal, content_id)
        task.setScheduled_month('*')
        task.setScheduled_day_of_month('*')
        task.setScheduled_hour('10')
        task.setScheduled_minute('5')

        current_date=DateTime('2004/10/30 10:16')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2004-10-31 10:05:00') == next_scheduled, DateTime('2004-10-31 10:05:00').ISO() + ' != ' + next_scheduled.ISO())

        current_date=DateTime('2004/10/31 10:16')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2004-11-01 10:05:00') == next_scheduled, DateTime('2004-11-01 10:05:00').ISO() + ' != ' + next_scheduled.ISO())

        current_date=DateTime('2004/11/30 10:16')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2004-12-01 10:05:00') == next_scheduled, DateTime('2004-12-01 10:05:00').ISO() + ' != ' + next_scheduled.ISO())

        # leap year
        current_date=DateTime('2004/02/28 10:16')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2004-02-29 10:05:00') == next_scheduled, DateTime('2004-02-29 10:05:00').ISO() + ' != ' + next_scheduled.ISO())

        # non-leap year
        current_date=DateTime('2005/02/28 10:16')
        next_scheduled = task.getNextScheduledExecutionTime(current_date)
        self.failUnless(DateTime('2005-03-01 10:05:00') == next_scheduled, DateTime('2005-03-01 10:05:00').ISO() + ' != ' + next_scheduled.ISO())


if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPloneMaintenance))
        return suite

