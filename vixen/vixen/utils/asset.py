


from pymel.all import *  # Pymel module
import config
import gittools
import iquence
reload(gittools)
reload(config)

import os
import uuid
import getpass
import shutil
import datetime
import base64
import re
import hashlib

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import json
#import threading
#from Queue import Queue


Git = gittools.Git



class Asset(Git):
    '''Every command or feature or costomization go here'''

    def __init__(self, *args):
        '''constuctor'''
        self.ws = os.path.dirname(workspace(q=1, rd=1))
        os.chdir(self.ws)
        self.version = config.version
        Git.__init__(self)  # init Git runtime libs
        self._base_jobs()  # some basic definitions

    def _base_jobs(self):
        '''Some basic settings'''
        self.dellist = []  # list of files to be deleted after final commit
        self.filelist = set()  #new empty filelist
        sep = os.path.sep
        self.setWs(self.ws)  # reset workspace
        self.vID = self.getVID()
        #self.updateGitDbInfo()  #TODO
        self.setRenderSettings()
        

    def updateGitDbInfo(self):
        '''Update gitdir prefs'''
        gitdir = '%s_%s' % (os.path.basename(self.ws), self.vID)
        #gtdb = self.db(db.prefs.name=='gitdir').select().first()
        #if not gtdb:
            #self.db.prefs.insert(name='gitdir', value=gitdir)
       # else:
            #gtdb.update_record(value=gitdir)
        #self.db.commit()


    def getVID(self):
        '''Get vID and asset info'''
        self.vID = None
        try:
            self.vID = fileInfo['vID']
        except KeyError:
            self.vID = str(uuid.uuid4())  # generate a new uniqe id for asset
            fileInfo['vID'] = self.vID  # set a new vexinID
            fileInfo['av'] = '0'  # set a new vexinID
            companyName = ''
            fileInfo['studio'] = companyName
            fileInfo['vixen'] = self.version

        #self.assetDb = self._getAssetFromDb()  # get the last shot in db
        self.assetHistoryDb = self.getAssetHistory(self.vID)
        #print len(self.assetHistoryDb)
        return self.vID

    def getAttachments(self, vID):
        '''Get attachments of assset'''
        data = self.db(self.db.attachs.vID == vID).select()
        #print data
        return data

    def setWs(self, ws):
        '''Set workspace'''
        #print 'ws is %s'%ws
        #self.ws = ws
        if not os.path.isdir(ws):  # If directory is deleted
            os.makedirs(ws)  # create that directory
        os.chdir(ws)
        self.defineProject(ws)
        workspace(ws, o=True)  # set the directory as current workspace for maya
        return ws

    def genCleanDate(self):
        '''generate a clean date line 28.03.2008'''
        self.now = datetime.datetime.now()
        day = self.now.day  # 31
        month = self.now.month  # 03
        year = self.now.year  # 2012
        vtime = '%d.%d.%s' % (day, month, str(year)[-2:])
        return vtime

    def _generateName(self):
        ''' Generates a standard file name base on below standard:
            <Custom name>__<person>_<software>_<date>_v<version>.<ext>
            - For maya Idecided to save all files as binary
            - date format is like: 31312
        '''
        vtime = self.genCleanDate()
        sn = sceneName()
        if sn:
            return sn
        else:
            #basename=sn.split('.')[0]
        #print sn
            basename = '_%s_Ma_%s_%s.mb' % (getpass.getuser()[:2].title(), vtime, fileInfo['vID'][:3])
        #print basename
            return basename

    def defineProject(self, workspace):
        '''Get a full workspace path and create project db for that'''
        projectdb = self.db(self.db.project.name == os.path.basename(workspace)).select().first()
        if not projectdb:  # if workspace is new:
            self.db.project.insert(name=os.path.basename(workspace), path=workspace)
        return projectdb



    def saveScene(self, description=None, *args):
        '''Save the scene and add it to db'''
        self.vID = self.getVID()
        self.setProg(3)
        if not os.path.dirname(workspace(q=1, rd=1)) == self.ws:
            if self.assetDb:
                fileInfo(rm='vID')
                fileInfo(rm='av')
            self.__init__()
            self.saveScene()  # init again

        self.setProg(5, 'Generating file name')
        name = self._generateName()
        self.setProg(7, 'Setting new version')
        version = len(self.assetHistoryDb) + 1
        fileInfo['av'] = str(version)  # update version +1
        #self.gitbranch(self.assetDb)  # switch to main branch before saving

        self.setProg(12, 'Get selection list')
        self.setSelection()
        self.setProg(15, 'Taking a snapshot')
        newThumb = self.snapshot()  # take a snapshot and save it to db.

        self.setProg(25, 'Finding Textures and resources')
        sm = dgmodified()
        if sm:
            modfs = len(sm)
            self.doTextures()
            self.setProg(40, 'Saving scene')
            self.expFile = saveAs(name, type='mayaBinary')  # , cmp=True)  # save file
            self.getUsedFiles()  # add used files to file list before saving (like textures, refernces, etc)
            self.setProg(60, 'Rechecking scene name')
            self.sceneName = workspace(pp=name)  # get the relative name: scenes/asda.mb
            #self.filelist.add(self.sceneName)  # add current file to git add list
            self.setProg(70, 'Adding information to local database')
            #print self.filelist
            os.chdir(self.ws)
            self.gitadd(self.assetDb, self.filelist)  # Add all files to git rep
            self.filelist=set()  #reset file list..
            self.setProg(85, 'Commiting changes')
            githash = self.gitcommit(adb=self.assetDb, modfs=modfs)  # get the hash number of commit
            #print githash
            self.setProg(90, 'Updating database')
            if githash:
                if not description:
                    description = textField('DiscriptionField', q=1, text=1)
                newG = self.db.git.insert(description=description, version=version, \
                    vID=self.assetDb.vID, thumb=newThumb, githash=githash,\
                    datetime=datetime.datetime.now(), name=self.sceneName)  # new git record
                self.setProg(95)
                #~ self.assetHistoryDb = self.getAssetHistory(self.assetDb.vID)
                newHL = self.assetDb.history + [newG]
                self.assetDb.update_record(history=newHL, current=newG, name=self.sceneName)  # add new record to asset history
                self.name = name
                self.addPrMenus()
                self.db.commit()  # commiting changes to database
                self.setProg(100, 'Done')
            else:
                warning('Vixen: error 115. There was an error!!!. ')
                self.db.commit()
                #sys.exit()
        else:
            self.setProg(100, 'Done')

    def saveLastRender(self):
        '''Save latest render in renderview to disk'''
        editors = [p for p in lsUI(p=1) if 'renderView' in p]
        if editors:  # If everything is correct
            editor = editors[-1]
            renderWindowEditor(editor, e=True, di=0)
            renderWindowEditor(editor, e=True, wi="test")

    def getAssetHistory(self, vID):
        '''Get git records relating to a asset'''
        self.assetDb = self._getAssetFromDb()
        self.attachments = self.getAttachments(self.assetDb.vID)
        self.assetHistoryDb = self.db(self.db.git.vID == self.assetDb.vID).select()  # history of asset
        return self.assetHistoryDb

    def _getAssetFromDb(self):
        '''Search database for latest version of asset and return it.'''
        self.assetDb = self.db(self.db.asset.vID == self.vID).select().last()  # search local database for this shot
        if not self.assetDb:
            #name = self._generateName()
            fileInfo(rm='vID')
            fileInfo(rm='av')
            self.vID = str(uuid.uuid4())  # generate a new uniqe id for asset
            fileInfo['vID'] = self.vID  # set a new vexinID
            fileInfo['av'] = '0'  # set a new vexinID
            #print 'Setting Name to: %s' % name
            self.assetDb = self.db.asset.insert(vID=self.vID, workspace=os.path.basename(self.ws))  # new record in database
            self.db.commit()  # commiting changes to database
        return self.assetDb

    def setRenderSettings(self):
        '''Set some require render settings.'''
        if getAttr("defaultRenderGlobals.imageFormat") != 32:
            setAttr("defaultRenderGlobals.imageFormat", 32)  # Set image format to png

    def getThumb(self):
        '''Get thumbnal address'''
        #self.setRenderSettings()
        st_dir = '%s%sstorage%s' % (self.storagepath, os.path.sep, os.path.sep)
        snapname = '%svixen_v%s_%s' % (st_dir, fileInfo['av'], fileInfo['vID'])
        #take a screenshot
        playblast(f=snapname, w=150, h=125, p=100, et=getCurrentTime(), st=getCurrentTime(), \
            os=1, fmt='image', fo=1, v=0, orn=0, compression='png')
        #now check for file availablity:
        storage_folder_contents = os.listdir(st_dir)
        isSnapEx = False
        snp = None  # snapshot imae
        for im in storage_folder_contents:
            if '_v%s_%s' % (fileInfo['av'], fileInfo['vID']) in im:
                isSnapEx = True  # image is available
                snp = im
        if not isSnapEx:  # if image is not available:
            raise(IOError)  # raise an error
        if snp:  # If there is any snapshot available:
            impath = st_dir + snp  # image full path
            #print impath
            return impath

    def snapshot(self):
        '''Create a snapshot of current active camera'''
        impath = self.getThumb()
        if impath:
            imdata = open(impath, 'rb').read()
            imdataEncode = base64.b64encode(imdata)
            fileInfo['vScreen'] = imdataEncode
            #print imdataEncode
            newThumb = self.db.vfile.insert(file=imdata)  # add file to db

            thmPath = self.genImgFromDb(fileId=newThumb)
            try:
                self.thumbImage.setImage(thmPath)
            except RuntimeError:
                pass
            #if self.assetDb: #if asset is defined in db:
            self.assetDb.update_record(thumb=newThumb)  # link the asset to this thumbnail.
            #print os.path.isfile(impath)
            try:
                os.remove(impath)
            except OSError:
                pass
            #now we add this file to dellist:
            #self.dellist.append(impath) #After comiting, dellist files will be delete
            return newThumb

    def genImgFromDb(self, fileId):
        '''Generate a temprary image file based on a database entery and return it's path'''
        filedb = self.db(self.db.vfile.id == fileId).select().last()  # it's image db
        thmbpath = '%s%sstorage%s.Thumb.png' % (self.storagepath, os.path.sep, os.path.sep)
        tmpImgFile = open(thmbpath, 'wb')  # open a file
        tmpImgFile.write(filedb.file)  # write image to it
        tmpImgFile.close()  # close th file
        return thmbpath  # return image path

    def AddFGMaps(self):
        '''Search for mentalray final gather files'''
        mraySet = set()
        try:
            pfgmap = getAttr('miDefaultOptions.finalGatherFilename')  # get primary final gather file name
            if pfgmap:  # if map name is available:
                pfgmap = '%s%srenderData%smentalray%sfinalgMap%s%s' % (self.ws, sep, sep, sep, sep, pfgmap)
                mraySet.add(pfgmap)
        except MayaAttributeError:
            pass
        try:
            phmap = getAttr('miDefaultOptions.photonMapFilename')  # get photon map file name
            if phmap:
                phmap = '%s%srenderData%smentalray%sphotonMap%s%s' % (self.ws, sep, sep, sep, sep, phmap)
                mraySet.add(phmap)
        except MayaAttributeError:
            pass
        for mrmap in mraySet:
            if os.path.isfile(mrmap):  # if file is available
                self.filelist.add(mrmap)  # Add map to git files list

    def doTextures(self):
        '''Search and add maya textue files'''
        #texture_types = set(['tif', 'tga', 'png', 'jpg'])
        for file_node in ls(type=('file')):  # find maya and mentalray files
            #print file_node
            #for i in dir(file_node):print i
            tex_path = getAttr("%s.fileTextureName" % file_node)
            is_sequence = getAttr('%s.useFrameExtension' % file_node)
            if not is_sequence:
                nfn = self.copyLocal(tex_path, 'sourceimages')
                if nfn:
                    setAttr('%s.fileTextureName' % file_node, nfn, type='string')  # Change fileTextureName attribute


    def getUsedTxs(self):
        '''Find missing textures'''
        mrf=set()
        for file_node in ls(type=('file')):  # find maya and mentalray files
            tex_path = getAttr("%s.fileTextureName" % file_node)
            is_sequence = getAttr('%s.useFrameExtension' % file_node)
            #print tex_path
            if tex_path and not is_sequence:
                tpath = 'sourceimages/%s' % os.path.basename(tex_path)
                mrf.add(tpath)
        #mrf=set(mrf)
        if mrf:
            return mrf
            
    
    def reloadTextures(self):
        '''Reload all texture files'''
        for tex in ls(type=('file')):
            cmd1 = 'showEditor %s' % tex
            cmd2 = 'AEfileTextureReloadCmd %s.fileTextureName;' % tex
            
            mel.evalDeferred(cmd1)
            mel.evalDeferred(cmd2)
 


    def getUsedFiles(self):
        '''Search for textture files and return as a list.'''
        sep = os.path.sep
        #workspace.mel file:
        #worksmel = '%s%sworkspace.mel' % (self.ws, sep)
        #print '___________>>>', self.filelist
        #if os.path.isfile(worksmel):
            #self.filelist.add(workspace(pp=worksmel))  # Add workspace.mel to project files



        mrf = cmds.file(q=True, list=True)


        mrf=set(mrf)
        #print mrf
        for f in mrf:
            self.copyLocal(f)

        #self.AddFGMaps()  # add mentaleay files to filelist
        self.doTextures()  #clean texture addresses
        #self.getRefs()
        #print self.filelist
        return self.filelist

    def setSelection(self):
        '''Find selected items and write them to 'vSel' fileinfo variable (comma separted)'''
        cList = ls(sl=1)  # Find current selected list
        cListSet = set()  # create a new set
        if cList:  # if list isnot empty:
            cListSet = set([str(sel) for sel in cList])
        #print cListSet
        selStr = ','.join(cListSet)
        fileInfo['vSel'] = selStr

    def copyLocal(self, file_path, local_folder=None):
        '''Copy a file that is not in workspace directery to given local folder'''
        #print 'processing %s' % file_path
        if not file_path:  #must be non-empty string
            return
        txlist = ['.tiff', '.tif', '.png', '.jpg', '.bmp', '.iff', '.exr', '.psd', \
                '.tga', '.tdl', '.hdr', '.ptx', '.rgb', '.pic', '.sgi']

        mslist = ['.mb', '.ma', '.obj']
        
        nfn = None

        ext = os.path.splitext(file_path)[-1].lower()
        sep = os.path.sep
        if not local_folder:
            if ext in txlist: local_folder = 'sourceimages'
            elif ext in mslist: local_folder = 'scenes'
            else: local_folder = 'data'

        if local_folder:
            abslf = '%s/%s' % (self.ws, local_folder)
            if not os.path.isdir(abslf):
                os.makedirs(abslf)
            
        #print file_path
        if self.ws not in file_path and os.path.isfile(file_path):  # file is located outside of project dir
            #print 'file is outside %s' % file_path
            file_name = os.path.basename(file_path)  #find base name
            #print file_name
            siDir = '%s%s%s%s' % (self.ws, sep, local_folder, sep)  #set dire
            if not os.path.isdir(siDir):  # create Source Images dir
                os.mkdir(siDir)
            nfn = siDir + file_name

            if not os.path.isfile(nfn):  # if file not copied before:
                shutil.copyfile(file_path, nfn)  # copy the file to new position in sourceimages
            nfn =  workspace(pp=nfn)

        elif  os.path.isfile(file_path):  # if file is available:
            #print 'file is inside %s' % file_path
            nfn = workspace(pp=file_path)
        #print 'generated: %s' % nfn
        if nfn:
            
            # copy to a well named file:
            if ext in txlist or (local_folder and ext not in mslist):
                nfol = os.path.abspath(os.path.dirname(nfn))
                bname = os.path.basename(nfn)
                suffix = self.vID.split('-')[0]
                newname = bname
                if not suffix in bname:
                    newname = 'V_%s_%s' % (suffix, bname)
                #src = '%s/%s/%s' % (self.ws, local_folder, bname)
                dst = '%s/%s/%s' % (self.ws, local_folder, newname)
                #print src, dst
                if not os.path.isfile(dst):
                    shutil.copyfile(file_path, dst)  # copy file
                
                ## clean
                #trashPath = '%s/%s' % (self.ws, nfn)
                #if os.path.isfile(trashPath):
                    #os.remove(trashPath)

                nfn = '%s/%s' % (local_folder, newname)
                #if local_folder and ext in mslist:
                    #self.sceneName = nfn  # change maya scene name to new one.
            #print dst
            #print 'Name is: %s' % nfn

            #print nfol

            self.filelist.add(nfn)
            return nfn

    def getAssetPath(self, dbname):
        '''Generate full path of asset file from database'''
        sep = os.path.sep
        prdb = self.db(self.db.project.name == dbname.workspace).select().last()
        wspath = prdb.path
        assetPath = '%s%s%s' % (wspath, sep, dbname.name)
        return assetPath

    def encodeImage(self, path):
        '''encode an image to base64'''
        if not os.path.isfile(path):
            warning('Vixen Error: Image is not available!')
            return
        else:
            bindata = open(path, 'rb').read()
            if bindata:  # if image is not empty:
                data = base64.b64encode(bindata)
                return data

    def embedImage(self, path):
        #path = '%s/%s' % (self.ws, i)
        data = self.encodeImage(path)  # encode image to string data
        ext = os.path.split(path)[-1].split('.')[-1]
        txtlist = ['jpg', 'png', 'tif', 'exr', 'hdr', 'bmp']
        if data and ext.lower() in txtlist:
            hashstr = hashlib.md5(data).hexdigest()
            #randStr = str(uuid.uuid4()).split('-')[0]
            keyname = 'vTex_%s_%s' % (hashstr, ext)
            keys = fileInfo.keys()
            target = [key for key in keys if key==keyname]
            if not target:
                fileInfo[keyname] = data
                return True

    
    def extractImage(self, keyname):
        '''Extract an image from encoded string'''
        endata = fileInfo[keyname]
        #endata += "="  # padding error fix
        #endata = endata.replace('\\n', '')  # padding error fix
        dstfolder = '%s/sourceimages/embedded' % self.ws
        if not os.path.isdir(dstfolder):
            os.makedirs(dstfolder)
        sym, fhash, ext = keyname.split('_')
        dstfile = '%s/%s.%s' % (dstfolder, fhash, ext)
        if not os.path.isfile(dstfile):
            data = base64.b64decode(endata)
            dst = open(dstfile, 'wb')
            dst.write(data)
            dst.close()


    def getIQuence(self, ws, depth=3):
        main = iquence.iQuence(str(os.path.abspath(ws)), depth=depth)
        #~ print main
        data = main.sequence(['*.png', '*.tif', '*.exr'])
        return data

    
    def getVserverInfo(self):
        vseq = None
        vshot = None
        try:
            vseq = fileInfo['vseq']
        except KeyError:
            pass
        try:
            vshot = fileInfo['vshot']
        except KeyError:
            pass
        return vseq, vshot

    def getMainCam(self):
        cameras = ls(type='camera', s=1)
        mainCamList = [i for i in cameras if i=='cameraMainShape']
        ## find cameraMain parent
        if mainCamList:
            mainCam = mainCamList[0].listRelatives(ap=1)
            if mainCam:
                if '%s.numberOfCameras'%mainCam[0] in mainCam[0].listAttr():
                    cam = mainCam[0]
                    return cam

    def getKeyFrameTimes(self, transform, attr):
        target = '%s.%s' % (transform, attr)
        data = keyframe(target, query=True, timeChange=True)
        return data
        
    def upload_to_server(self, file_path, thumbpath, duration, cuts=[], \
            vseq=None, vshot=None, st=0, et=0):
        '''Upload a file to vixen server'''
        server = self.db(self.db.prefs.name == 'server').select().first().value
        
        register_openers()
        request_page = "%s/utils/upload_from_maya.json" % server

        fd = open(file_path, "rb")
        tu = open(thumbpath, "rb")
        sha1 = hashlib.sha1(fd.read()).hexdigest()
        tusha1 = hashlib.sha1(tu.read()).hexdigest()
        if vshot:
            datagen, headers = multipart_encode({'prfile': fd, 'thumb':tu, 'sha1':sha1, \
                    'auth':self.get_vAuth(), 'frames':duration, 'tusha1':tusha1,\
                    'st':st, 'et':et, 'shotuuid':vshot})
        elif vseq:
            datagen, headers = multipart_encode({'prfile': fd, 'thumb':tu, \
                    'auth':self.get_vAuth(), 'frames':duration, 'sha1':sha1, \
                    'cuts':cuts, 'tusha1':tusha1, 'sequuid':vseq})
        
        else:
            warning('Vixen Error: Scene not assigned.')
            return
        # Create the Request object:confirm bd

        request = urllib2.Request(request_page, datagen, headers)
        data = urllib2.urlopen(request).read()
        feedback = json.loads(data)
        if feedback['result'] == 'ok':
            print feedback['info']
        else:
            warning('Vixen Server Error: %s' % feedback['info'])
        #feedback = json.loads(data)
        #print feedback

    def sendPr(self, *args):
        '''Get a playbast and send it to server'''
        # Register the streaming http handlers with urllib2
        vseq, vshot = self.getVserverInfo()
        if not (vseq or vshot):
            warning('Vixen Error: Scene not assigned to any sequence or shot yet!')
        else:
            scenePath = workspace(pp=sceneName())
            cuts = list()
            if vseq:
                self.setPathSeqOnServer(vseq, scenePath)
                check = self.getSeqInfoFromUUID(vseq)
                mayafps = check['mayafps']
                fps = check['fps']
                mainCam = self.getMainCam()
                if mainCam:
                    cuts=self.getKeyFrameTimes(mainCam, 'cameraNumber')
                    if cuts:
                        cuts[0] = 1.0  # fix for a problem
                        start_range = playbackOptions(q=1, min=1)
                        cuts = [cut for cut in cuts if cut >= start_range]
                        print(cuts)
                        numOfShots = check['numOfShots']
                        while numOfShots < len(cuts):
                            self.createShotOnServer(vseq)
                            numOfShots+=1
                        shots = self.getSeqInfoFromUUID(vseq)['shots']
                        print(shots)
                        shotdict = dict()
                        for shot in shots:
                            #print shots
                            shotdict[shot['number']] = shot['uuid']
                        for i in cuts:
                            try:
                                next_cut = int(cuts[cuts.index(i)+1]-1)
                            except IndexError:  #last cut
                                next_cut = int(playbackOptions(q=1, max=1))
                            #print shotdict
                            output_path, thumbpath = self.getPlayblast(st=int(i), et=next_cut, rate=fps, inrate=mayafps)
                            if output_path and thumbpath:
                                self.upload_to_server(output_path, thumbpath, \
                                        duration=next_cut-i+1, cuts=[], vseq=None, \
                                        vshot=shotdict[cuts.index(i)+1], \
                                        st=int(i), et=next_cut)
                        return

                
            if vshot:
                check = self.getShotInfoFromUUID(vshot)
                self.setPathShotOnServer(vshot, scenePath)  # update scene path
                mayafps = check['mayafps']
                fps = check['fps']
            et = int(playbackOptions(q=1, max=1))
            st = int(playbackOptions(q=1, min=1))
            duration = et-st
            #print 'Rate= %s' % fps
            output_path, thumbpath = self.getPlayblast(st=st, et=et, rate=fps, inrate=mayafps)
            if output_path and thumbpath:
                self.upload_to_server(output_path, thumbpath, duration, cuts, \
                        vseq, vshot, st=st, et=et)


    def getPlayblast(self, st, et, rate, inrate):
        tmp_loc = '%s/.tmp' % self.ws
        if not os.path.isdir(tmp_loc):
            os.mkdir(tmp_loc)
        rnd_suffix = str(uuid.uuid4()).replace('-', '')
        snapname = '%s/VixenServerPreview_%s' % (tmp_loc, rnd_suffix)
        input_path =  snapname + '_r' + '.%04d.png'
        output_path = '%s.m4v' % snapname
        ####
        playblast(f=snapname, st=st, et=et, w=852, h=480, \
                p=100, os=1, fmt='image', fo=1, v=0, orn=False, \
                compression='png', fp=4, cc=1)
        blast_files = self.fix_sequence_name(snapname, st=st, et=et, fmt='png')
        ffmpegpath = 'ffmpeg'

        sep = os.path.sep
        if os.name == 'nt':
            ffmpegpath = '%s%sutils%sbin%sffmpeg.exe' % \
                    (self.vixenpath, sep, sep, sep)
        elif os.name == 'posix':
            ffmpegpath = '%s%sutils%sbin%sffmpeg' % \
                    (self.vixenpath, sep, sep, sep)
        ffmpeg_convert_cmd = '"%s" -r %s -sameq -pix_fmt yuv420p -i "%s" -r %s -y "%s"' % \
                (ffmpegpath, inrate, input_path, rate, output_path)
        #ffplay_play_cmd = 'ffplay "%s"' % output_path
        print ffmpeg_convert_cmd
        (stdout, stderr) = self.process(ffmpeg_convert_cmd)
        if stderr:  # ffmpeg outputs to stderr
            #self.remove_files(blast_files)  #delete blast files
            thumbpath = '%s.thumb.png' % snapname
            thumbarg = '"%s" -i "%s" -r 1 -vframes 1 -sameq -s 256x144 -y "%s"' \
                % (ffmpegpath, output_path, thumbpath)  # removed -ss 1 becuase of a error
            #print thumbarg
            self.process(thumbarg)
            return (output_path, thumbpath)
        else:
            return (None, None)

    def remove_files(self, files):
        ''' remove files from disk'''
        for i in files:
            os.remove(i)

    def fix_sequence_name(self, path, st, et, fmt):
        ''' fix sequence name for ffmpeg convertion '''
        newfiles = set()
        st = int(st)
        et = int(et)
        #print st, et
        for i in range(st, et+1):
            namestd = '%s.%s.%s'
            numpad = '%s%s' % ((4 - len(str(i))) * '0', i)
            x = int(i-st+1)
            #print i
            #print x
            newpad = '%s%s' % ((4 - len(str(x))) * '0', x)
            oldname = namestd % (path, numpad, fmt)
            newname = namestd % (path+'_r', newpad, fmt)
            #print 'Renaming "%s" to "%s"' % (oldname, newname)
            #shutil.move(oldname, newname)
            os.renames(oldname, newname)
            newfiles.add(newname)
            #print oldname
            #print newname
        return newfiles

    def getJsonData(self, url):
        ''' Get JSON data'''
        server = self.db(self.db.prefs.name == 'server').select().first().value
        keychar = '?'
        if '?' in url:
            keychar = '&'
        #url = urllib2.quote(url)
        dataurl ='%s/%s%sauth=%s' % (server, url, keychar, self.get_vAuth())
        dataurl = dataurl.replace(' ', '%20')  # fix for some errors
        #print dataurl
        try:
            data = urllib2.urlopen(dataurl).read()
        except urllib2.URLError:
            print('Vixen: Trying to fetch information from: %s' % dataurl)
            warning('Vixen: Vixen Server is down or wrong proxy settings.')
            return

        newdata = json.loads(data)
        if newdata['result'] == 'ok':
            return newdata
        else:
            warning('Vixen Server Error: %s' % newdata['result'])
            if 'info' in newdata.keys():
                warning('Vixen Info: %s' % newdata['info'])

    def openBasedOnNumbers(self, prid, seqNum, shotNum=None):
        '''Open scene file based on shot or sequence info on vixen server'''
        url ='utils/getScenePathJSON.json?prid=%s&seqNum=%s&shotNum=%s' % \
            (prid, seqNum, shotNum)
        data = self.getJsonData(url)
        return data['scenePath']

    def setPathShotOnServer(self, shotid, scenePath):
        '''Sets scene file path for a shot on vixen server'''
        url ='utils/setPathShotDataJSON.json?shotid=%s&scenePath=%s' % \
            (shotid, scenePath)
        data = self.getJsonData(url)
        return data

    def setPathSeqOnServer(self, sid, scenePath):
        '''Sets scene file path for a shot on vixen server'''
        url ='utils/setPathSeqDataJSON.json?sid=%s&scenePath=%s' % \
                (sid, scenePath)
        data = self.getJsonData(url)
        return data

    def createShotOnServer(self, sid):
        '''Get projects information from Vixen Server'''
        url ='utils/createShot.json?sid=%s' % (sid)
        data = self.getJsonData(url)
        return data


    def getPrDataFromServer(self, *args):
        '''Get projects information from Vixen Server'''
        url ='utils/getProjectsDataJSON.json'
        projects = self.getJsonData(url)
        return projects

    def getSeqDataFromServer(self, prid, *args):
        '''Get Sequence information from Vixen Server'''
        url ='utils/getSeqsDataJSON.json?pr=%s' % prid
        seqs = self.getJsonData(url)
        return seqs

    def getShotDataFromServer(self, prid, seq, *args):
        '''Get Shots information from Vixen Server'''
        url ='utils/getShotsDataJSON.json?seq=%s&prid=%s' \
                % (seq, prid)
        shots = self.getJsonData(url)
        return shots

    def getShotUUID(self, prid, seqnum, shotnum, *args):
        ''' Get a shot uuid from server based on numbers'''
        url = 'utils/getShotUUID.json?prid=%s&seqnum=%s&shotnum=%s' % \
                (prid, seqnum, shotnum)
        data = self.getJsonData(url)
        return data

    def getSeqUUID(self, prid, seqnum, *args):
        ''' Get a shot uuid from server based on numbers'''
        url = 'utils/getSeqUUID.json?prid=%s&seqnum=%s' % (prid, seqnum)
        data = self.getJsonData(url)
        return data

    def getShotInfoFromUUID(self, shotuuid, *args):
        ''' get shot info from server based on a uuid'''
        url = 'utils/getShotInfoFromUUID.json?uuid=%s' % shotuuid
        data = self.getJsonData(url)
        return data

    def getSeqInfoFromUUID(self, sequuid, *args):
        ''' get seq info from server based on a uuid'''
        url = 'utils/getSeqInfoFromUUID.json?uuid=%s' % sequuid
        data = self.getJsonData(url)
        return data

    def get_vAuth(self):
        '''Get vAuth from db'''
        vAuthdb = self.db(self.db.prefs.name=='vAuth').select().first()
        return vAuthdb.value






