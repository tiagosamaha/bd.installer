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
Main external methods that are part of our proposed scripts collection
"""
__version__ = "$Revision: 23767 $"
# $Source$
# $Id: MaintenanceToolbox.py 23767 2006-05-19 14:28:16Z roeder $
__docformat__ = 'restructuredtext'


from StringIO import StringIO
import time
from DateTime import DateTime

#from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent


# Timeit function stolen from ATContentTypes 1.0/tool/migration.py
def timeit(data=None):
    """Measure real time and cpu time of an event

    returns real time, cpu time as tuple
    """
    if data is None:
        return time.time(), time.clock()
    else:
        return time.time() - data[0], time.clock() - data[1]


# ############################################################
# 1/ packDB - Pack Zope Database ('main' db if none is specified)
# ############################################################

def packDB(self, dbname='main', days=0):
    """Rebuilding all catalogs"""

    out = StringIO()

    dbs = self.Control_Panel.Database
    if dbname in dbs.getDatabaseNames():
        try:
            dbs[dbname].manage_pack(days=days)
        except:
            # FIXME - Add exception handling
            pass
        print >> out, "Zope database '%s' has been packed" % dbname

    return out.getvalue()


# #########################################
# 2/ archiveExpiredContent
# #########################################

def archiveExpiredContent(self, dest_path='/archives', meta_type='', query_path=''):
    """Move expired contents to archives repository"""

    out = StringIO()

    portal_url = self.portal_url
    portal = portal_url.getPortalObject()
    portal_catalog = self.portal_catalog
    archived = []

    archives_path = '/'.join(portal.getPhysicalPath()) + dest_path
    try:
        archFolder = self.unrestrictedTraverse(archives_path)
    except:
        raise "Please, create the archives folder at '%s', and restart" % archives_path

    now = DateTime()
    query = {'expires': {'query': now,
                         'range': 'max'},
             'review_state': 'published',
            }

    # Optional query elements
    if meta_type:
        query['meta_type'] = meta_type
    if query_path:
        query['path'] = query_path

    archiving_brains = portal_catalog(query)
    ##return len(archiving_brains)           # Only for testing purpose.

    for brain in archiving_brains:
        obj = brain.getObject()

        if obj is None:
            continue

        obj_info = "%s : %s [expired on %s]" % (brain.getPath(), obj.Title(), obj.ExpirationDate())
        archived.append(obj_info)  # Used for the report

        # Now, archive it !
        parentFolder = aq_parent(obj)
        temp = parentFolder.manage_cutObjects([obj.getId()])
        archFolder.manage_pasteObjects(temp)

    if len(archived):
        print >> out, "%s expired content(s) archived\n" % len(archived)
        print >> out, '\n'.join(archived)
    else:
        print >> out, "No expired content has been found matching your request\n"

    return out.getvalue()


# #########################################
# 3/ rebuildCatalogs - Rebuilding all catalogs
# #########################################
#
# Requires Archetypes >= 1.3.1

try:
    from Products.PloneArticle.PloneArticle import PloneArticle
except ImportError, e:
    HAS_PLONE_ARTICLE = False
else:
    HAS_PLONE_ARTICLE = True

def rebuildCatalogs(self):
    """Rebuilding all catalogs
       A different approch is explained here:
       http://www.zopezen.org/Members/andy/source_code.2005-10-09.3475932214/silvercity_view
    """

    out = StringIO()

    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()
    portal_types = getToolByName(self, 'portal_types')
    portal_catalog = getToolByName(self, 'portal_catalog')
    uid_catalog = getToolByName(self, 'uid_catalog')
    reference_catalog = getToolByName(self, 'reference_catalog')
    basepath = '/'.join(portal.getPhysicalPath())

    # Find all Plone/CMF content meta_types
    factory_meta_type = 'Factory-based Type Information'
    all_meta_types = [factory.Metatype()
                      for factory in portal_types.objectValues(spec=factory_meta_type)]
    print >> out, "CMF/Plone types found:", ', '.join(all_meta_types)

    # 1/ Clear all catalogs (Reset)
    portal_catalog.manage_catalogClear()
    uid_catalog.manage_catalogClear()
    reference_catalog.manage_catalogClear()

    print >> out, "'portal_catalog', 'reference_catalog', and 'uid_catalog' have been cleared"

    # 2/ Find all available content objets and add them in the catalog
    #    This mean uid_catalog and reference_catalog should also get updated (by the same catalog call)
    #    This can be costly.

    timeinfo = timeit()

    # Tried this method first. But ref and uid catalogs are not getting updated
    # in my tests on a Plone 2.0.5 / AT 1.3.3 / ATCT 2.0-based site.
    # Both catalogs were empty after the script was executed.
    # So I moved to the other method below.
    # TODO : Write unit tests for an understanding of this kind of mystery.

    #contents = portal.ZopeFindAndApply(portal,
    #                                   obj_metatypes=all_meta_types,
    #                                   search_sub=1,
    #                                   REQUEST=self.REQUEST,
    #                                   apply_func=portal_catalog.catalog_object,
    #                                   apply_path=basepath)

    contents = portal.ZopeFindAndApply(portal,
                                       obj_metatypes=all_meta_types,
                                       search_sub=1,)
    for content_id, content_obj in contents:
        content_obj.indexObject()

    elapse, c_elapse = timeit(timeinfo)
    count = len(contents)

    print >> out, "Catalog has been repopulated with %s objects (in %s seconds - cpu %s seconds)" % (count, elapse, c_elapse)

    # 3/ Unindex all that's inside PloneArticle and subclasses
    if HAS_PLONE_ARTICLE:
        # find all meta types for PloneArticle and subclasses
        archetype_tool = getToolByName(self, 'archetype_tool')
        at_registered = archetype_tool.listRegisteredTypes()
        pa_meta_types = [t['meta_type'] for t in at_registered
                         if (issubclass(t['klass'], PloneArticle)
                             and
                             t['meta_type'] in all_meta_types)]

        article_brains = portal_catalog(portal_type=pa_meta_types)

        threshold = 2000
        count = 0

        for article_brain in article_brains:
            count = count + 1
            article = article_brain.getObject()

            # Unindex subcontents of the article
            for obj in article.objectValues():
                portal_catalog.unindexObject(obj)

            # ZODB trick stolen from Zopelabs.org (Thx Alan) :
            # When dealing with TONS of objects in ZODB...
            # the trick is to deactivate the objects and at some threshold
            # possibly do a ZODB cache minimize.
            # This will help keep the memory footprint reasonable.
            article._p_deactivate()

            if (count % threshold) == 0:
                portal_catalog._p_jar.cacheMinimize()
                count = 0

        print >> out, "PloneArticle and subclasses subcontent (files, images) have been unindexed"

    return out.getvalue()

# #########################################
# 4/ updateCatalog - Update portal catalog
# #########################################
#
# Requires Archetypes >= 1.3.1

def updateCatalog(self):
    """Update the portal catalog"""
    out = StringIO()
    portal_catalog = getToolByName(self, 'portal_catalog')
    timeinfo = timeit()
    # Update portal catalog
    portal_catalog.refreshCatalog(clear=1)
    elapse, c_elapse = timeit(timeinfo)
    print >> out, "'portal_catalog' has been updated (in %s seconds - cpu %s seconds)" % (elapse, c_elapse)
    return out.getvalue()

# ############################################################
# 5/ brokenScript - A script producing an error at each execution. Used for testing purposes.
# ############################################################

def brokenScript(self):
    """Failing script"""
    print failingtoprintthis

# ############################################################
# 5/ workingScript - A script working at each execution. Used for testing purposes.
# ############################################################

def workingScript(self):
    """Working script"""
    pass
