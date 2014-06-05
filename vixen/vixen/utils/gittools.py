

import os
import sys
import re
import datetime
import getpass
import vdata
from Queue import Queue
import config
from threading import Thread, Lock
from subprocess import Popen, PIPE, call  # everything nedded to handle external commands
import webbrowser as wb


Vdata = vdata.Vdata


class Git(Vdata):
    '''Git python port'''
    screen_mutex = Lock()
    def __init__(self, *args, **kw):
        '''constructor'''
        self.vixenpath = config.getpath(storage=None)
        self.storagepath = config.getpath()
        sep = os.path.sep
        Vdata.__init__(self, self.storagepath)
        self.gitexe = 'git'
        if os.name == 'nt':  # for windoows users
            self.gitexe = '%s%sutils%sWGit%sbin%sgit' % (self.vixenpath, sep, sep, sep, sep)
        self.filelist = set()  # all files that we will add to git.


    def getGitDir(self):
        '''Create a git directory for each project'''
        sep = os.path.sep
        namedir = '%s_%s' % (os.path.basename(self.ws), self.vID)
        gitdir = '%s%sstorage%s%s' % (self.storagepath, sep, sep, namedir)  # every workspace has it's own git dir
        if not os.path.isdir(gitdir):
            os.mkdir(gitdir)

        return gitdir

    def quote_command(self, cmd):
        if not (os.name == "nt" or os.name == "dos"):
            return cmd # the escaping is required only on Windows platforms, in fact it will break cmd line on others
        re_quoted_items = re.compile(r'" \s* [^"\s] [^"]* \"', re.VERBOSE)
        woqi = re_quoted_items.sub('', cmd)
        if len(cmd) == 0 or (len(woqi) > 0 and not (woqi[0] == '"' and woqi[-1] == '"')):
            return '"' + cmd + '"'   
        else:
            return cmd

    def process(self, execfn):
        '''General external process'''
        cmd = self.quote_command(execfn)  #preventing windows base errors
        p = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE,
                )
                #universal_newlines=True)  # process
        (stdout, stderr) = p.communicate()
        return (stdout, stderr)

    def getAssetProject(self, adb):
        #print type(adb)
        ws = adb.workspace
        prdb = self.db(self.db.project.name == ws).select().first()
        #print prdb
        return prdb

    def execute(self, adb, args=[], v=False):
        '''Command excution pipeline'''
        self.gitdir = self.getGitDir()
        sep = os.path.sep
        wsname = adb.workspace
        prdb = self.getAssetProject(adb)
        ws = prdb.path
        execfn = ' '.join(['%s --git-dir="%s" --work-tree="%s"' % \
            (self.gitexe, self.gitdir, ws)] + list(args))
        #print execfn
        if v:  # verbose mode
            try:
                self.lastEC.setText(execfn)
            except RuntimeError:
                pass
        data = self.process(execfn)
        if not data[1]:  # if there is no stderr
            return data[0] # return stdout
        else:
            print '*'*30 + ' Vixen Error ' + '*'*30
            print data[1]
            print '*'*74

    def openFile(self, filepath):
        '''Open a file with associated program'''
        if sys.platform.startswith('darwin'):  # for osx support
            call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            call(('xdg-open', filepath))

    def sha1sum(self, fpath):
        '''Find sha1 checksum of a given file'''
        if not os.path.isfile(fpath):
            return
        if sys.platform == 'linux2':
            arg = 'sha1sum "%s"' % fpath
        #elif sys.platform == 'win32':
        #    fciv = '%s%sutils%sWSha1%sfciv' % (path, sep, sep, sep, sep)

        sha1 = self.process(arg)
        if sha1 and not 'No such file or directory' in sha1:  # If we have true sha1 of file
            return sha1.split()[0]

    def executeExternal(self, command):
        '''Excute a command outside of maya and dont wait for it's result'''
        p = Popen(command, shell=False, env=os.environ, stdout=None, stdin=None, close_fds=True)  # proces

        return p.pid

    def gitinit(self, adb):
        '''Initialize the project git rep'''
        self.execute(adb, ['init -q'])  # It's important to initalize before working with git.
        #self.execute(['gc']) #cleanup
        #print self.execute(['branch'])

    def getUntracked(self, adb):
        '''analize the status and return a list of untracked files to add.'''
        stat = self.gitstatus(adb)
        data = stat.split('\n')
        untlist = set()
        for line in data:
            if '??' in line:
                relpath = ' '.join(line.split()[1:])
                untlist.add(relpath)
        return untlist

    def getHashDic(self, adb):
        '''generate a dic of full and short hashes'''
        arg = ['log', '--pretty=format:"%h %H"']
        rawdata = self.execute(adb, arg)
        rawList = rawdata.split('\n')
        hashdic = dict()
        for line in rawList:
            lit = line.split()
            hashdic[lit[0]] = lit[1]
        return hashdic

    def findFullHash(self, adb, shorthash):
        '''Find complete hash of object'''
        hashdic = self.getHashDic(adb)
        return hashdic[shorthash]

    def getUntrackedTypes(self, adb, typ):
        '''Finf untrack files based on file types'''
        mslist = []
        if typ == 'maya':
            mslist = ['.mb', '.ma', '.obj']
        elif typ == 'textures':
            mslist = ['.tiff', '.tif', '.png', '.jpg', '.bmp', '.iff', '.exr', '.psd', \
                '.tga', '.tdl', '.hdr', '.ptx', '.rgb', '.pic', '.sgi']
        elif typ == 'shaders':
            mslist = ['.sl', '.slo', '.sdl', '.mat']
        elif typ == 'cache':
            mslist = ['.mc', '.ptc', '.bkm', '.ptc']
        untlist = self.getUntracked(adb)
        data = [res for res in untlist if os.path.splitext(res)[-1].lower() in mslist]
        return data


    def getUntrackedScenes(self, adb):
        '''Find untracked maya files'''
        #os.path.splitext(a)
        return self.getUntrackedTypes(adb, typ='maya')

    def gitadd(self, adb, filelist):
        '''Add files to library'''
        self.gitinit(adb)
        if filelist:
            flist = '"%s"' % '" "'.join(filelist)  # "'/home/farsheed/Ubuntu One"/home/farsheed/1023824.mp4.st'"
            #print '_'*80
            #print flist
            #print '_'*80
            arg = ['add', '-f', flist] #generate argument
            self.execute(adb, arg, v=True)  # run

    def gitarchive(self, adb, version, outName):
        '''Archive a head or branch as a single zip file'''
        #branch = adb.vID
        #version = adb.current
        githash = self.getRecordHash(adb, version)
        #print githash
        if githash:
            args = ['archive', '--format=zip', '-0', githash, '>', '"%s.zip"' % outName]
            self.execute(adb, args)
            return self.explore(adb)

    def gitstatus(self, adb):
        '''Get status of what is going on for the scenefile'''
        status = self.execute(adb, ['status -s'])
        return status

    def explore(self, adb):
        '''Explre a folder using default viwer'''
        aPath = self.getAssetProject(adb).path
        wb.open(aPath)  # Seems a cross platform solution.

    def gitlog(self, adb):
        '''Get a log'''
        log = self.execute(adb, ['shortlog "%s"' % self.sceneName])
        return log

    def gitreflog(self, adb):
        '''get a full log of hashes'''
        arg = ['reflog']
        reflog = self.execute(adb, arg)
        return reflog

    def gitconfig(self):
        '''
            git config --global user.name "Your Name"
            git config --global user.email you@example.com
        '''
        login = getpass.getuser()
        exefn1 = '%s config --global user.name "%s"' % (self.gitexe, login)
        exefn1 = '%s config --global user.email "%s@vixen.local"' % (self.gitexe, login)
        self.process(exefn1)
        self.process(exefn2)

    def gitcommit(self, adb, modfs=None, sole=False, \
                message=str(datetime.datetime.now())):
        '''Commit changes to your files.'''
        message = '"vID: %s, Version: %s, Modified: %s nodes, Datetime: %s"' \
            % (adb.vID, len(adb.history)+1, modfs, message)
        arg2 = ['commit', '-am', message]
        if sole:
            arg2.append('"%s"' % adb.name)  # only commit this file, not others.

        newcommit = self.execute(adb, arg2, v=True)  # run commit
        #print 'commit message is: %s' % newcommit
        if newcommit:
            #hashmatch = re.search('[\s\w\d]+', newcommit )
            part1 = newcommit.split(']')[0]
            if part1:
                part2 = part1.split()[-1]
                if part2:
                    githash = part2
                    if not 'track' in githash and len(githash) == 7:  # if it's a sha1 hash:
                        fullhash = self.findFullHash(adb, githash)
                        return fullhash
                    else:
                        return

    def getRecordHash(self, adb, version=None):
        '''get a record base on assetDb and version number'''
        if version:
            record = self.db((self.db.git.vID == adb.vID) & (self.db.git.version == version)).select().last()
        else:
            record = self.db(self.db.git.vID == adb.vID).select().last()
        if record:
            return record.githash

    def gitcheckout(self, adb, version=None, filelist=None):
        '''Restore the file base on a version'''
        #print adb.name, version
        #print filelist
        aPath = self.getAssetProject(adb).path
        githash = self.getRecordHash(adb, version)
        #print 'Git Hash is: %s' % githash
        if githash:
            arg = ['checkout', '-fq', githash]

            if filelist:
                flist = '"%s"' % '" "'.join(filelist)
                arg.append(flist)
            else:
                arg.append('"%s"' % adb.name)

            self.execute(adb, arg, v=True)  # restore
            fpath = '%s%s%s' % (aPath, os.path.sep, adb.name)
            return fpath

    def gitbranch(self, adb):
        '''Create a new branch for the scene and check it out'''
        branch = adb.vID

        blist = self.execute(adb, ['branch -a']).split()
        if branch in blist:  # branch is available
            bindex = blist.index(branch)
            if bindex and blist[bindex - 1] == '*':  # The branch is selected already, no need to switch
                #print 'ooooooooohhhhhhhhhhhhhhhhhhhhhhhh'
                return
            else:  # Branch is available but not active. need to switch
                arg = ['checkout -fq', branch]
        else:  # Need to create the branch and switch
            arg = ['checkout -bq', branch]
        self.execute(adb, arg)

    def gitlist(self, adb):
        '''List all the files in git repo'''
        arg = ['ls-files']
        files = self.execute(adb, arg)
        return files
