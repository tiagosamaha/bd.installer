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

# Don't change this file in your product!
#
# This file is currently copied manually from the "common" product
# to the product before each release, so changes have to be made
# in the "common" product
#
# http://cvs.sourceforge.net/cgi-bin/viewcvs.cgi/ingeniweb/common/
#
# This code will soon be integrated into either QuickInstaller, so
# this is an intermediary solution.

from cStringIO import StringIO
import string
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFPlone.migrations.migration_util import safeEditProperty

try:
    from Products.Localizer.Localizer import manage_addLocalizer
    from Products.Localizer.MessageCatalog import manage_addMessageCatalog
    import Products.TranslationService
    hasLocalizer = 1
except ImportError:
    hasLocalizer = 0

try:
    import Products.i18n
    hasi18n = 1
except:
    hasi18n = 0

from zLOG import INFO, ERROR
from Products.CMFCore.utils import getToolByName 

class Installation:
    def __init__(self, root):
        self.root=root
        self.out=StringIO()
        self.typesTool = getToolByName(self.root, 'portal_types')
        self.skinsTool = getToolByName(self.root, 'portal_skins')
        self.portal_properties = getToolByName(self.root, 'portal_properties')
        try:
            self.navigation_properties = self.portal_properties.navigation_properties
        except:
            pass
        try:
            self.form_properties = self.portal_properties.form_properties
        except:
            pass

    def report(self):
        self.out.write('Installation completed.\n')
        return self.out.getvalue()

    def setupTools(self, product_name, tools):
        addTool = self.root.manage_addProduct[product_name].manage_addTool
        for tool, title in tools:
            found = 0
            for obj in self.root.objectValues():
                if obj.meta_type == tool:
                    found = 1
            if not found:
                addTool(tool, None)

            found = 0
            root=self.root
            for obj in root.objectValues():
                if obj.meta_type == tool:
                    obj.title=title
                    self.out.write("Added '%s' tool.\n" % (tool,))
                    found = 1
            if not found: 
                self.out.write("Couldn't add '%s' tool.\n" % (tool,))

    def installSubSkin(self, skinFolder):
        """ Install a subskin, i.e. a folder/directoryview.
        """
        for skin in self.skinsTool.getSkinSelections():
            path = self.skinsTool.getSkinPath(skin)
            path = map( string.strip, string.split( path,',' ) )
            if not skinFolder in path:
                try:
                    path.insert( path.index( 'custom')+1, skinFolder )
                except ValueError:
                    path.append(skinFolder)
                path = string.join( path, ', ' )
                self.skinsTool.addSkinSelection( skin, path )
                self.out.write('Subskin successfully installed into %s.\n' % skin)    
            else:
                self.out.write('*** Subskin was already installed into %s.\n' % skin) 

    def setupCustomModelsSkin(self, skin_name):
        """ Install custom skin folder
        """
        try:
            self.skinsTool.manage_addProduct['OFSP'].manage_addFolder(skin_name + 'CustomModels')
        except:
            self.out.write('*** Skin %sCustomModels already existed in portal_skins.\n' % skin_name)
        self.installSubSkin('%sCustomModels' % skin_name)

    def setupTypesandSkins(self, fti_list, skin_name, install_globals, fti_list2=None):
        """
        setup of types and skins
        """
        if self.hasFormController() and fti_list2:
            fti_list = fti_list2

        # Former types deletion (added by PJG)
        for f in fti_list:
            if f['id'] in self.typesTool.objectIds():
                self.out.write('*** Object "%s" already existed in the types tool => deleting\n' % (f['id']))
                self.typesTool._delObject(f['id'])

        # Type re-creation
        for f in fti_list:
            # Regular FTI processing
            cfm = apply(FactoryTypeInformation, (), f)
            self.typesTool._setObject(f['id'], cfm)
            self.out.write('Type "%s" registered with the types tool\n' % (f['id']))

        # Install de chaque nouvelle subskin/layer
        try:  
            addDirectoryViews(self.skinsTool, 'skins', install_globals)
            self.out.write( "Added directory views to portal_skins.\n" )
        except:
            self.out.write( '*** Unable to add directory views to portal_skins.\n')

        # Param de chaque nouvelle subskin/layer
        self.installSubSkin(skin_name)

    def isPlone2(self,):
        """
        isPlone2(self,) => return true if we're using Plone2 ! :-)
        """
        return self.hasFormController()        

    def hasFormController(self,):
        """
        hasFormController(self,) => Return 1 if CMFFC is available
        """
        if 'portal_form_controller' in self.root.objectIds():
            return 1
        else:
            return None

    def addFormValidators(self, mapping):
        """
        Adds the form validators.
        DON'T ADD ANYTHING IF CMFFORMCONTROLLER IS INSTALLED
        """
        # Plone2 management
        if self.hasFormController():
            return
        for (key, value) in mapping:
            safeEditProperty(self.form_properties, key, value)

    def addNavigationTransitions(self, transitions):
        """
        Adds Navigation Transitions in portal properties
        """
        # Plone2 management
        if self.hasFormController():
            return
        for (key, value) in transitions:
            safeEditProperty(self.navigation_properties, key, value)

    def setPermissions(self, perms_list, roles = ['Manager', 'Owner', ]):
        """
        setPermissions(self) => Set standard permissions / roles
        """
        # As a default behavior, newly-created permissions are granted to owner and manager.
        # To change this, just comment this code and grab back the code commented below to
        # make it suit your needs.
        for perm in perms_list:
            self.root.manage_permission(
                perm,
                tuple(roles),
                acquire = 1
                )
        self.out.write("Reseted default permissions\n")

    # Adapted from Plone 2.0 setup/languages.py
    def setupLocalizer(self):
        """
        setupLocalizer(self) => Setup Localizer
        
        Adds Localizer and translation_service.
        """
        self.out.write('Installing Localizer\n')
        if 'Localizer' not in self.root.objectIds():
            manage_addLocalizer(self.root, 'Localizer', ('en',))

        self.out.write('Installing TranslationService\n')
        if 'translation_service' not in self.root.objectIds():
            self.root.manage_addProduct['TranslationService'].addPlacefulTranslationService('translation_service')

        self.out.write('Removing accept_path\n')
        lObj = self.root._getOb('Localizer')
        lObj.accept_methods = ['accept_cookie',]

    # Adapted from Plone 2.0 setup/languages.py
    def setupMessageCatalog(self, i18n_name):
        """
        setupMessageCatalog(self) => Setup Message Catalog
        
        Set up languages from the product i18n folder
        using Localizer and Translation Service
        """
        self.out.write('Adding Message Catalog in Localizer\n')
        lObj = self.root._getOb('Localizer')
        manage_addMessageCatalog(lObj, i18n_name, '%s Message Catalog' %i18n_name, 'en')

        self.out.write('Set Domain Info in Translation Service\n')
        tObj = self.root._getOb('translation_service')
        tObj.manage_setDomainInfo(None, path_0='%s/%s' % ('Localizer', i18n_name))

        self.out.write('Deleting all languages in Message Catalog, just in case\n')
        mObj = lObj._getOb(i18n_name)
        mObj.manage_delLanguages(languages=mObj._languages)

    # Adapted from Plone 2.0 setup/languages.py
    def addLanguages(self, mName, files_by_language, default_language='en'):
        """
        addLanguages(self) => Add Languages
        """
        mObj = self.root._getOb('Localizer')._getOb(mName)
        for language, file in files_by_language.items():
            try:
                mObj.manage_addLanguage(language)
                mObj.manage_import(language, file)
                self.out.write('Adding language: %s\n' % language)
            except:
                self.out.write('Failed to setup .po file for: %s\n' % file)

        self.out.write('Set the default language\n')
        mObj.manage_changeDefaultLang(language=(default_language,))

    def addActionIcon(self, category, action_id, icon_expr, title=None, priority=0):
        # Add the action icon if and only if it's not already here
        ai=getToolByName(self.root, 'portal_actionicons')
        if not ai.queryActionInfo( category, action_id ):
            ai.addActionIcon(category, action_id, icon_expr, title, priority)
