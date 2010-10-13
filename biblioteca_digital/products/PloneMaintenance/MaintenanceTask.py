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
Maintenance Task
"""
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from global_symbols import *
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import SimpleItemWithProperties
from DateTime import DateTime
import traceback

from Products.PloneMaintenance.PloneMaintenanceTool import getNoSecDate

try:
    from Products.CMFCore.CMFCorePermissions import View
except:
    from Products.CMFCore.permissions import View

# Plone2 FTI
factory_type_information = {
  'id'             : 'MaintenanceTask',
  'portal_type'    : 'MaintenanceTask',
  'meta_type'      : 'MaintenanceTask',
  'description'    : 'A MaintenanceTask',
  'content_icon'   : 'task.gif',                          # Icon has to be acquired from a skin folder
  'product'        : 'PloneMaintenance',
  'factory'        : 'addMaintenanceTask',
  'immediate_view' : 'MaintenanceTask_edit2',
  'filter_content_types' : 0,                                   # This is for folderish types
  'allowed_content_types': (),                                  # If filter_content_types is true, this field can hold allowed meta_types
  'actions': (),
  }


# The usual factory
def addMaintenanceTask(self, id, title = '', REQUEST = {}):
    """
    Factory method for a MaintenanceTask object
    """
    obj = MaintenanceTask(id, title)
    self._setObject(id, obj)

    if REQUEST.has_key('RESPONSE'):
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_main')

class MaintenanceTask(SimpleItemWithProperties):
    """MaintenanceTask class"""

    #                                                                           #
    #                            BASIC CLASS BEHAVIOUR                          #
    #                                                                           #

    meta_type = "MaintenanceTask"

    global_allow   = 0

    manage_options = SimpleItemWithProperties.manage_options

    month_selection=('*','1','2','3','4','5','6','7','8','9','10','11','12')

    #day_of_week_selection=('*','1','2','3','4','5','6','7')

    day_of_month_selection=('*','1','2','3','4','5','6','7','8','9',
                            '10','11','12','13','14','15','16','17',
                            '18','19','20','21','22','23','24','25',
                            '26','27','28','29','30','31')

    hour_selection=('*','0','1','2','3','4','5','6','7','8','9','10',
                    '11','12','13','14','15','16','17','18','19','20',
                    '21','22','23')

    minute_selection=('*','0','1','2','3','4','5','6','7','8','9','10',
                      '11','12','13','14','15','16','17','18','19','20',
                      '21','22','23','24','25','26','27','28','29','30',
                      '31','32','33','34','35','36','37','38','39','40',
                      '41','42','43','44','45','46','47','48','49','50',
                      '51','52','53','54','55','56','57','58','59')

    # Standard security settings
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)            # $$$ Is this clever ? Isn't it better to make the object private ?
                                                                        # This method makes all class properties & methods protected by View by default

    security.declarePrivate('manage_afterAdd')
    def __init__(self, id, title=''):
        """Initialize properties"""

        self.id = id
        self.title = title

        # Properties to be edited by site manager
        self._setProperty('scheduled_month', 'month_selection', 'selection')
        self.setScheduled_month('*')

        #self._setProperty('scheduled_day_of_week', 'day_of_week_selection', 'selection')
        #self._updateProperty('scheduled_day_of_week','*')

        self._setProperty('scheduled_day_of_month', 'day_of_month_selection', 'selection')
        self.setScheduled_day_of_month('*')

        self._setProperty('scheduled_hour', 'hour_selection', 'selection')
        self.setScheduled_hour('*')

        self._setProperty('scheduled_minute', 'minute_selection', 'selection')
        self.setScheduled_minute('*')

        self._setProperty('script_name','getScripts','selection')

        self._setProperty('notified_emails', [], 'lines')

        self.resetLastExecutionDate()


    def resetLastExecutionDate(self):
        self.last_execution_date = DateTime(2000, 1, 1)

    def getScripts(self,):
        scripts = ['Select a script']
        scripts = scripts + getToolByName(self, 'portal_maintenance').scripts.keys()
        return scripts

    def runScript(self, script, force=0):
        if force==1:
            script(force)
        else:
            # Call without the parameter for backwards compatability
            script()

    def sendNotificationEmail(self, start_date, end_date, msg, failed):
        """Send a summary of the task processing to emails addresses.

        Returns true if an email is sent else false

        @param start_date: Start of the processing
        @param end_date: End of the processing
        @param msg: Returned message after task processing
        @param failed: True if task has failed while processing
        """

        # Get emails to notify
        to_emails = getattr(self, 'notified_emails', [])
        if not to_emails:
            return False

        host = self.MailHost

        # Render the email
        for to_email in to_emails:
            mail_text = self.pm_task_mail_template(
                           to_email=to_email,
                           start_date=start_date,
                           end_date=end_date,
                           msg=msg,
                           failed=failed)

            # Send email
            try:
                host.send(mail_text)
            except:
                Log(LOG_DEBUG, "Error while sending email on task %s" % self.getId())

    def runTask(self, date=None, force=0):
        # Always runs task as it does not check if pending
        date = getNoSecDate(DateTime())
        script_name = getattr(self,'script_name', None)
        Log(LOG_DEBUG, "Running script %s due %s at %s" % (
            script_name,
            self.getNextScheduledExecutionTime(date),
            date,
            ))
        run=0
        if script_name:
            pm = getToolByName(self, 'portal_maintenance')
            script = pm.scripts.get(script_name)
            if script:
                msg = ''
                failed  = False
                start_date = DateTime()
                try:
                    self.runScript(script, force=force)
                    Log(LOG_DEBUG, "Done running script", script_name)
                    run = 1
                except Exception, error_msg:
                    tbuffer = StringIO()
                    traceback.print_exc(file=tbuffer)
                    msg = tbuffer.getvalue()
                    tbuffer.close()
                    failed = True
                    Log(LOG_DEBUG, "Failed running script %s with error: %s", (script_name, error_msg))

                end_date = DateTime()
                self.sendNotificationEmail(start_date, end_date, msg, failed)
                self.last_execution_date = date
            else:
                Log(LOG_DEBUG, "Couldn't get script", script_name)
        else:
            Log(LOG_DEBUG, "Couldn't get script_name", script_name)
        return run

    def getLastExecutionTime(self):
        return self.last_execution_date

    def getNextScheduledExecutionTime(self, current_date):
        # Return the date at which the task was last scheduled
        # Input: current_date
        # Output: The earlies date after the current date at which the task should be executed

        current_date = getNoSecDate(current_date)

        c_year, c_month, c_day, c_hour, c_minute, c_seconds, c_zone = current_date.parts()

        # Minute
        if self.scheduled_minute == '*':
            if self.scheduled_day_of_month != '*' or self.scheduled_month != '*' or self.scheduled_hour!='*':
                next_minute = 0
            else:
                next_minute = c_minute
        else:
            next_minute = int(self.scheduled_minute)

        # Hour
        if self.scheduled_hour == '*':
            if self.scheduled_day_of_month != '*' or self.scheduled_month != '*':
                next_hour = 0
            else:
                next_hour = c_hour
        else:
            next_hour = int(self.scheduled_hour)

        # Increase hour if necessary
        if self.scheduled_hour == '*':
            if not (self.scheduled_day_of_month != '*' or self.scheduled_month != '*'):
                if (c_hour, c_minute) > (next_hour, next_minute):
                    next_hour = c_hour + 1
                    if next_hour > 23:
                        next_hour = 0

        # Day of month
        if self.scheduled_day_of_month == '*':
            if self.scheduled_month != '*':
                next_day=1
            else:
                next_day=c_day
        else:
            next_day = int(self.scheduled_day_of_month)

        # Increase day of month if necessary
        if self.scheduled_day_of_month == '*':
            if not self.scheduled_month != '*':
                if (c_day, c_hour, c_minute) > (next_day, next_hour, next_minute):
                    next_day = c_day + 1
                    if c_month in (1, 3, 5, 7, 8, 10, 12) and next_day > 31:
                        next_day = 1
                    elif c_month in (4, 6, 9, 11) and next_day > 30:
                        next_day = 1
                    elif  c_month == 2:
                        is_leap_year = DateTime(c_year, c_month, c_day).isLeapYear()
                        if (is_leap_year and next_day > 29) or \
                           (not is_leap_year and next_day > 28): 
                               next_day = 1

        # Month
        if self.scheduled_month == '*':
            next_month = c_month
        else:
            next_month = int(self.scheduled_month)

        # Increase month if necessary
        if self.scheduled_month == '*':
            if (c_month, c_day, c_hour, c_minute) > (next_month, next_day, next_hour, next_minute):
                next_month = next_month + 1
                if next_month > 12:
                    next_month = 1

        # Year
        next_year = c_year

        # Increase year if necessary
        if (c_year, c_month, c_day, c_hour, c_minute) > (next_year, next_month, next_day, next_hour, next_minute):
            next_year += 1
        date_string = "%d/%02d/%02d %02d:%02d" % (next_year, next_month, next_day, next_hour, next_minute)

        try:
            return DateTime(date_string)
        except DateTime.DateError:
            return DateTime('2500/12/31 00:00')

    def isPending(self, date=None):
        """ Return 1 if task is pending, 0 else

        If the task was already run in this intervall, do nothing
        Otherwise run the task if the current date falls in this intervall
        """

        if not date:
            date = getNoSecDate(DateTime())
        else:
            date = getNoSecDate(date)

        pending = False

        current_next_scheduled = self.getNextScheduledExecutionTime(date)
        last_next_scheduled = self.getNextScheduledExecutionTime(self.getLastExecutionTime())

        if last_next_scheduled < current_next_scheduled:
            if last_next_scheduled <= date:
                pending = True

        elif last_next_scheduled == current_next_scheduled:
            # Was already executed for this schedule
            pending = False

        elif last_next_scheduled > current_next_scheduled:
            # Bad initialization date ?
            pending = False

        if self.scheduled_month == '*' and self.scheduled_day_of_month == '*' and \
           self.scheduled_hour == '*' and self.scheduled_minute == '*':
            # Execute anytime so this is pending whatsoever
            pending = True

        return pending

    def setScheduled_month(self, month):
        if month in self.month_selection or str(month) in self.month_selection:
            self._updateProperty('scheduled_month', str(month))
        else:
            raise ValueError

    def setScheduled_day_of_month(self, day):
        if day in self.day_of_month_selection or str(day) in self.day_of_month_selection:
            self._updateProperty('scheduled_day_of_month', str(day))
        else:
            raise ValueError

    def setScheduled_hour(self, hour):
        if hour in self.hour_selection or str(hour) in self.hour_selection:
            self._updateProperty('scheduled_hour', str(hour))
        else:
            raise ValueError

    def setScheduled_minute(self, minute):
        if minute in self.minute_selection or str(minute) in self.minute_selection:
            self._updateProperty('scheduled_minute', str(minute))
        else:
            raise ValueError

    def setScript_name(self, script_name):
        self._updateProperty('script_name', script_name)
        #if script_name in self.getScripts():
        #    self._updateProperty('script_name', script_name)
        #else:
        #    raise ValueError

InitializeClass(MaintenanceTask)
