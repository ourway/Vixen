import maya.cmds as mc
from pymel.core import *
import os
import sys
import time
from dal import *
import uuid
import hashlib
import datetime


class Worker:
    '''Main class of worker'''
    def __init__(self, server_ip, dbname, dbusr, dbpwd):
        '''Constructor'''
        #print('Vixen Server IP is: %s' % server_ip)
        self.server_ip = server_ip
        self.dbname = dbname
        self.dbusr = dbusr
        self.dbpwd = dbpwd
        #print('Trying to connect to "%s" with "%s" user...' % (dbname, dbusr))
        self.connect()
        self.define()

    def connect(self):
        ''' Connect to server database '''
        #sphere()
        arg = "postgres://%s:%s@%s:5432/%s" % (self.dbusr, self.dbpwd, self.server_ip, self.dbname)
        #print arg
        self.db = DAL(arg, pool_size=10, check_reserved=['postgres', 'mssql'], migrate=False)
        #print db
        #auth = Auth(db)
        #crud, service, plugins = Crud(db), Service(), PluginManager()

    def define(self):
        '''define tables'''

        now=datetime.datetime.now()


        self.db.define_table('vfile',
            Field('uuid', length=64, default=uuid.uuid4()),
            Field('datetime', 'datetime', default=now),
            Field('name', length=256),
            Field('type', length=32, default='file'),
            Field('rawname', length=256),
            Field('m4v', length=256), # for videos
            Field('mpg', length=256), # for videos
            Field('cache', length=256),
            Field('thumb', 'integer', default=None),  #for videos
            Field('ext', length=64),
            Field('hash', length=256),
            Field('frames', 'integer', default=0),
            Field('data', 'blob'),
            #Field('process', self.db.process),
            #Field('uploader', db.auth_user, default=auth.user_id),
            Field('isvideo', 'boolean', default=False),
            )
        #print self.db(self.db.vfile.id).select()
        #self.db.commit()

        


