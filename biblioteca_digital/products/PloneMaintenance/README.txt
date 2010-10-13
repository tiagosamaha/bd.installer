PloneMaintenance

PloneMaintenance consists of a portal_maintenance tool that  allows you to 
define maintenance tasks and scripts to run according to a schedule assigned
to the tasks. 

No task is going to be run unless it is scheduled to. The schedule information
is stored in the task, and even if PloneMaintenance is called many times in a
row, it will always look up the schedule information, check when was the last
time the task was run, calculate the next time the task is scheduled to run,
and depending on this, PloneMaintenance will decide whether it runs the script
associated to the task or not. 

PloneMaintenance depends on an external tool to wake it up and make it execute
the scheduled tasks. Without an external tool, PloneMaintenance will just sit
and wait, doing nothing. You can go to the portal_maintenance tool and manually
run the maintenance tasks, but most of the time, you want an external tool doing
the job automatically.

You can choose one of the Schedulers which are available for Zope, or call 
PloneMaintenance from a cron job. 

Zope 2.6:
* http://www.zope.org/Members/lstaffor/Xron

Zope 2.7:
* http://dev.legco.biz/products/ZopeScheduler
* http://dev.legco.biz/products/timerservice

Hint on timerservice installation under windows
-----------------------------------------------

This product installation requires to compile a python module. This
compilation *do not* need to Visual C++ being installed. You just need
to compile the module with the python used for your Plone installation.
Go in $Plone\Products\TimerService\timerserver\ and run:

"C:\Program Files\Plone-2.x\Zope\bin\python.exe" setup.py install

Now windows didn't link correctly your module. You have to copy/paste
the module in "C:\Program Files\Plone-2.x\Zope\lib\python".


Setup runMaintenanceTasks script
--------------------------------

All the schedulers have to do is call the runMaintenanceTasks Python
Script that will take care of calling the runTasks method of the
portal_maintenance tool. The runMaintenanceTasks script can be run
by an anonymous user, because the PloneMaintenance tool makes sure
to only run tasks that need to be run.

Another way of calling PloneMaintenance is by an unix cron job. All you 
need to do is to call http://mysite.com/runMaintenanceTasks every 
once in a while. Have a look at the following Howto on Zope.org: 

Run cron jobs to do things  automatically
http://zope.org/Members/phd/cron-zope


How PloneMaintenance works
--------------------------

When the PloneMaintenance tool is called, it locks itself using the _v_running 
variable. The next time a schedule is started, this lock will prevent the 
execution of the Tasks so that tasks that take a long time to execute are
protected.

When a Task is created, an initial execution time is stored, although this
does not mean we start the Task right away.

The PloneMaintenance tool executes one Task after the other, always storing the
execution date. At the end, the lock is removed.

PloneMaintenance computes the next execution time given the current date and
compares it to the next execution date, given the last execution date. If the
two calculated dates are the same, it does nothing, otherwise it runs the task.

Tasks are added to the portal_maintenance tool. They have a "script_name" property
that names the script which they execute, and they have a "last_execution_date",
which stores the last time the task was executed.

Scripts are also added to the portal_maintenance tool. They can be normal Python
Scripts.

Here is an example of a Maintenance Script for a Plone site::

  # Script for packing the ZODB:
  # (Already integrated into PloneMaintenance)

  dbs=context.Control_Panel.Database
  if 'main' in dbs.getDatabaseNames():
      try:
          dbs['main'].manage_pack(days=0)
      except:
          pass


Installation
------------

  Install PloneMaintenance from the Plone Configlet or using the QuickInstaller.
  
  Note : Once you have an instance of the PloneMaintenanceTool, you should 
  avoid uninstalling PloneMaintenance, otherwise you will lose any custom 
  scripts and tasks. 

Further information
-------------------

  API Documentation:

    See http://ingeniweb.sourceforge.net/Products/PloneMaintenance/api/PloneMaintenance.html

  Information about PloneMaintenance can be found at:

    http://ingeniweb.sourceforge.net/Products/PloneMaintenance
