from Testing.makerequest import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from zope.component import getUtility
from nsi.metadataextractor.interfaces import (IMetadataExtractor,IMetadataExtractorSettings)
from nsi.officetransforms.interfaces import IOfficeTransformsConnection
from nsi.officetransforms.interfaces import IOfficeTransformsSettings
from nsi.grainextractor.interfaces import IGrainExtractorTool, IGrainExtractorSettings
from optparse import OptionParser
import transaction

parser = OptionParser()

parser.add_option("-p", "--portal_id", dest="portal_id",
                  help="ID do portal da BD",
                  default="bd")

parser.add_option("-u", "--initial-user",dest="user_and_pass",
                  help="Usuario e password, separados por :",
                  default="zope:zope")

parser.add_option("-o", "--oood-hostname", dest="oood_hostname_and_port",
                  help="Hostname e port do Oood separados por :",
                  default="localhost:8011")

(options, args) = parser.parse_args()

username, password = options.user_and_pass.split(':')
oood_hostname, oood_port = options.oood_hostname_and_port.split(':')
portal_id = options.portal_id

app = makerequest(app)
if hasattr(app, portal_id):
    raise AttributeError, "%s already exists!" % portal_id

user = app.acl_users.getUserById(username)
if user is None:
  uf = app.acl_users
  uf._doAddUser(username, password, ['Manager',], [])
  user = uf.getUserById(username)

newSecurityManager(None, user.__of__(app.acl_users))

app.manage_addProduct['CMFPlone'].addPloneSite(id=portal_id)
plone_site = getattr(app, portal_id)
portal_quickinstaller = plone_site.portal_quickinstaller
portal_quickinstaller.installProduct("nsi.digitallibraryinstaller")

transaction.commit()

metadataextractor_settings = getUtility(IMetadataExtractorSettings)
metadataextractor_settings.hostname = oood_hostname
metadataextractor_settings.port = oood_port

grainextractor_settings = getUtility(IGrainExtractorSettings)
grainextractor_settings.hostname = oood_hostname
grainextractor_settings.port = oood_port

officetransforms_settings = getUtility(IOfficeTransformsSettings)
officetransforms_settings.hostname = oood_hostname
officetransforms_settings.port = oood_port

transaction.commit()

