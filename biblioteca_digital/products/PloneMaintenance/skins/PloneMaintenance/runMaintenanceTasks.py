## Script (Python) "runMaintenanceTasks"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Run Maintenance Tasks
return context.portal_maintenance.runTasks()

