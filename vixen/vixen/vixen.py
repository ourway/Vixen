#!/usr/bin/env mayapy

__Author = 'Farsheed Ashouri'
__Owner = 'Vishka Animation Studio'
__copyright = __Owner

## DEV: Developments notes go here:

'''
Developed in MAYA 2014, Linux.
'''

## Description

## Usage
'''
In your script directory, create "userSetup.py" and
copy these lines in it:
#=========================
from pymel.all import *
from vixen import vixen
vixen.runVixen()
#=========================
'''


from pymel.all import *
from utils import vgui
from utils import config
#from utils import cherrypy
import maya.cmds as mc
import datetime
import time
import os
import threading
from utils.pyftpdlib import ftpserver
import getpass
import urllib
import webbrowser as wb

Vgui = vgui.Vgui
ws = os.path.dirname(workspace(q=1, rd=1))


class Ftp(threading.Thread):
    '''Run ftp server'''
    def __init__(self):
        threading.Thread.__init__(self)
        self.ws = os.path.dirname(workspace(q=1, rd=1)).split('/')[-1]

    def run(self):
        user = str(getpass.getuser())
        authorizer = ftpserver.DummyAuthorizer()
        authorizer.add_user(user, "12345", 'storage/%s' % str(self.ws), perm="elradfmw")
        #authorizer.add_anonymous("/home/farsheed/server/web2py/applications/vixenserver/static/uploads/nobody")
        handler = ftpserver.FTPHandler
        handler.authorizer = authorizer
        address = ("0.0.0.0", 29897)
        ftpd = ftpserver.FTPServer(address, handler)
        ftpd.serve_forever()


class checkVersion(threading.Thread):
    '''Run update checker'''
    def __init__(self, db):
        threading.Thread.__init__(self)
        self.db = db

    def run(self):
        link = 'http://vixen.alwaysdata.net/vixen/static/data/version'
        try:
            data = urllib.urlopen(link)
        except IOError:
            return
        version = data.read().split('\n')[0]
        try:
            fversion = float(version.replace('.', ''))
            foldVersion = float(config.version.replace('.', ''))
        except ValueError:  # In a cause internet is available but gives wrong data
            fversion = None

        if fversion and fversion > foldVersion:
            warning('A new version of Vixen is available for download: %s' % version)
            ulink = 'http://vixen.alwaysdata.net/vixen/home/upgrade?old=%s&new=%s' % (config.version, version)

            dbname = 'vcheck_%s' % config.version

            if not self.db(self.db.prefs.name == dbname).select().first():
                wb.open(ulink)
                self.db.prefs.insert(name=dbname)
                self.db.commit()


def cmport():
    '''Open a command port'''
    newPort = 29999
    try:
        data = commandPort(eo=1, n='0.0.0.0:%d' % newPort, bs=256000000, \
            po=True, stp='python')
        return data

    except RuntimeError:
        warning("Vixen Can't open command port.")
        return

def show():
    #print 'Renewing Vixen'
    gui = Vgui()
    gui.show()
    #gui.vOpen()

def reloadGui():
    '''reload vixen GUI'''
    if frameLayout('Vixen', ex=1):
        deleteUI('Vixen')
    showVwin()

def runVixen():
    '''Run Vixen in script job mode'''
    scriptJob(e=('PreFileNewOrOpened', show), per=True)
    evalDeferred(cmport)


if __name__ == '__main__':
    showVwin()
