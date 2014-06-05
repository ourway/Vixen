

from dal import *  # Database abstration Layer module
import datetime
import os
import sys
import uuid
import getpass
import license
import config
reload(license)
reload(config)

License = license.License
now = datetime.datetime.now  # for using like now()


class Vdata(License):
    '''Data base options. This class must be software independent'''

    def __init__(self, path, *args, **kw):
        '''constructor'''

        #First check license, Then continue
        #self.chkLicense()
        ###
        #self.las_super = super(Vdata, self)
        #self.las_super.__init__(*args)
        License.__init__(self)  # run license tool
        self.chkLicense()
        self.folder = path
        self.username = getpass.getuser()
        try:
            self._connect()  # connect to local database
            #self._define()  #base definitions
            self._build()  # base definitions
            self.db.commit()  # save chenges for the first time.
        except OperationalError:
            sys.exit()  # close the application.

    def _connect(self):
        '''Build, initialize or connect to local database.'''
        #Check the folder structure:
        #print locals()['self.db']
        storageLoc = '%s%sstorage' % (self.folder, os.path.sep)  # The folder in witch we will save/read database
        if not os.path.isdir(storageLoc):  # if there is no folder
            try:
                os.mkdir(storageLoc)  # create
            except IOError:
                raise  # stop
        #connect to database:
        self.db = DAL('sqlite://%s%sstorage%sVixenStorage.sqlite' % \
            (self.folder, os.path.sep, os.path.sep))

        #print self.db._uri
    def _define(self):
        '''Create some tables for database'''

        self.db.define_table('prefs',
            Field('datetime', 'datetime', default=now()),
            Field('name', length=32),
            Field('value', length=356),
            )

        self.db.define_table('person',
            Field('datetime', 'datetime', default=now()),
            Field('name', length=64, default=self.username),
            Field('nicename', length=64, default=self.username),
            Field('uuid', length=64, default=uuid.uuid4),
            Field('prefs', self.db.prefs),
            )

        self.db.define_table('vfile',
            Field('datetime', 'datetime', default=now()),
            Field('uuid', length=64, default=uuid.uuid4()),
            Field('file', 'blob'),
            )

        self.db.define_table('git',
            Field('datetime', 'datetime', default=now()),
            Field('uuid', length=64, default=uuid.uuid4()),
            Field('vID', length=64),  # vID of asset
            Field('githash', length=32),
            Field('name', length=128),
            Field('branch', length=32),
            Field('description', length=256, default=''),
            Field('thumb', self.db.vfile),  # thumbnail of version
            Field('version', 'integer', default=1),
            )

        self.db.define_table('project',
            Field('datetime', 'datetime', default=now()),
            Field('uuid', length=64, default=uuid.uuid4()),
            Field('name', length=128),
            Field('path', length=256),
            )

        self.db.define_table('attachs',
            Field('datetime', 'datetime', default=now()),
            Field('uuid', length=64, default=uuid.uuid4()),
            Field('vID', length=64),
            Field('description', length=256),
            Field('name', length=256),
            Field('path', length=512),
            Field('opened', 'integer', default=0)
            )

        self.db.define_table('asset',
            Field('datetime', 'datetime', default=now()),
            Field('uuid', length=64, default=uuid.uuid4()),
            Field('vID', length=64),
            Field('workspace', length=64),
            Field('description', length=256),
            Field('name', length=128),
            Field('label', length=128),
            Field('filepath', length=512),
            Field('tags', length=128),
            Field('disabled', 'boolean', default=False),
            Field('current', self.db.git),
            Field('history', 'list:reference', self.db.git, default=[]),  # related git records
            Field('attachments', 'list:reference', self.db.attachs, default=[]),  # Scene attachments and resources
            Field('thumb', self.db.vfile),  # latest thumbnail of asset
            )

        #self.db.attachs.name.requires = IS_NOT_IN_DB(self.db, 'attachs.name')

    def _build(self):
        '''Build essential structure of database'''
        self._define()
        #create person database
        settingsdb1 = self.db(self.db.prefs.id).select().first()
        if not settingsdb1:
            settingsdb1 = self.db.prefs.insert()  # create new one

        serverdata = self.db(self.db.prefs.name=='server').select().first()
        if not serverdata:
            self.db.prefs.insert(name='server', value='http://vixenserver:8000/vixenserver')

        vAuthdb = self.db(self.db.prefs.name=='vAuth').select().first()
        if not vAuthdb:
            newvAuth = str(uuid.uuid4()).replace('-', '')
            self.db.prefs.insert(name='vAuth', value=newvAuth)

        persondb = self.db(self.db.person.name == self.username).select().first()
        if not persondb:  # if there is no user matching current login:
            self.db.person.insert(name=self.username, prefs=settingsdb1)  # add new one
            self.prefsdb = settingsdb1  # define our pref settings
        else:
            self.prefsdb = self.db(self.db.prefs.id == persondb).select().first()
