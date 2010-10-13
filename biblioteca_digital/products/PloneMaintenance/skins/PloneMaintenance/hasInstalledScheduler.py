## Script (Python) "hasInstalledScheduler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Has Installed Scheduler
installed=0
for product in ['Xron', 'ZopeScheduler', 'ZScheduler']:
    if context.portal_quickinstaller.isProductInstalled(product):
        installed=1
return installed