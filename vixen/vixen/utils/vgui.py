
from pymel.all import *  # Pymel module
import asset
import config
from vutils import prettydate as pd
import sys
import os
import webbrowser as wb
import base64
import iquence

vipath = os.path.dirname(__file__)
#print vipath
sys.path.append(vipath)
#from vutils import Timer as Timer
#import threading
#from Queue import Queue
Asset = asset.Asset

class Vgui(Asset):
    '''building main gui'''

    def __init__(self, *args, **kw):
        '''Constructor'''
        print 'Vgui constructing ...'
        #print 'initing gui'
        Asset.__init__(self)  # init Asset
        self.report = []
        
        self.logo = '%s/storage/.vLogo.png' % (self.storagepath)
        self.icon = '%s/storage/.vIcon.png' % (self.storagepath)
        config.logo(self.logo)  # Generate logo
        config.icon(self.icon)  # Generate logo

    def after(self):
        '''Do this jobs after loading vixen. mostly some GUI updates'''
        #print 'Vixen: Updating Interface...'
        self.smartSel(mode='fl')
        #time.sleep(5)

    def webserver(self):
        '''Run web2py webserver engine'''

    def getRec(self, version):
        '''Returns the record database of scene based on it's version number'''
        self.getVID()
        for his in self.assetHistoryDb:  # iterate in histories:
            if his.version == int(version):
                return his

    def stextc(self, *args):
        '''This method will be run when selection is changed.'''
       # print 'selecttttiiinnnggg'
        if self.vlistSc.getSelectItem():  # If there is any seletion:
            sver = int(self.vlistSc.getSelectItem()[0].split('.')[0])  # first selection
            sdb = self.getRec(sver)  # get record db
            #print sver
            if sdb:  # if we found the record:
                sThumId = sdb.thumb  # we got thumbnal file db id
                thmPath = self.genImgFromDb(fileId=sThumId)  # now we generate a tmp image of thumbnal
                self.thumbImage.setImage(thmPath)  # set Image
                desc = sdb.description.title()
                self.descriptionText.setLabel(desc)
                self.hisDate.setLabel(pd(sdb.datetime))  # write pretty date
                    #Now we need to find the related database

    def rac(self, *args):
        '''Get the command and execute it'''
        if self.assetDb:
            command = self.actext.getText()
            data = self.execute(self.assetDb, [command], v=True)
            if data:
                print data

    def setHud(self, label):
        '''Creates an hud for given label'''
        if headsUpDisplay('VixenHUD', ex=1):
            headsUpDisplay('VixenHUD', e=1, l=label)
        else:
            headsUpDisplay('VixenHUD', s=1, b=1, dfs='large', p=30, bs='large', ba='center', dw=50, l=label)

        headsUpDisplay('VixenHUD', r=1)  # refresh

    def setProg(self, num, status='Calculating...'):
        '''Set Vixen progress bar in nice way'''
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
        progressBar( gMainProgressBar,
                            edit=True,
                            beginProgress=True,
                            isInterruptable=True,
                            status=status,
                            maxValue=100 )
        for i in range(num) :
            if progressBar(gMainProgressBar, query=True, isCancelled=True ) :
                break
            progressBar(gMainProgressBar, edit=True, step=1)
        if num == 100:
            progressBar(gMainProgressBar, edit=True, endProgress=True)

    def dctextc(self, *args):
        '''double click on text command'''
        if self.vlistSc.getSelectItem():
            sver = int(self.vlistSc.getSelectItem()[0].split('.')[0])  # first selection
            self.setProg(5, 'Checking out')
            print self.assetDb
            file_name = self.gitcheckout(self.assetDb, sver)  # restore to previous version
            self.setProg(15, 'Reading Local Database')
            record = self.db((self.db.git.vID == self.assetDb.vID) & (self.db.git.version == sver)).select().first()
            self.setProg(25, 'Upgrading records')
            self.assetDb.update_record(current=record)  # Update asset current version
            self.db.commit()
            self.setProg(35, 'Reading Scene File')
            #print file_name
            openFile(file_name, force=True, iv=1)  # refresh the file
            self.setProg(75, 'Reloading textures')
            self.reloadTextures()
            self.setProg(85, 'Setting HUD')
            self.setAssetHud(record)
            self.setProg(90, 'Refreshing GUI')
            #self.updateVlist()
            self.smartSel()
            self.setProg(100, 'Done')
            
            #print 'checking for changes ...'
            self.gitcheckout(self.assetDb, sver, self.getUsedTxs() )  # restore files
            #reload missed ones:
            #fnodes = ls(type=('file', 'mentalrayTexture'))  #find file nodes
            #for i in fnodes:
                #mel.eval('AEfileTextureReloadCmd %s.fileTextureName;' % i)  # reload textures.

    def setAssetHud(self, record):
        '''Set HUD based on information of a record'''
        descHud = 'version %s - %s' % (record.version, record.description)
        if not record.description:
            descHud = descHud.split(' - ')[0]  # remove " - " from HUD
        self.setHud(descHud)

    def updateAssignProjects(self, *args):
        '''Get projects list from server and add it to V.S. pr list'''
        self.serverPrList.removeAll()  # clean the list
        self.serverSeqList.removeAll()
        self.serverShotList.removeAll()
        #self.serverSeqList.setDisable()
        #self.serverShotList.setDisable()

        projects = self.getPrDataFromServer()  # get project list
        if projects:
            projectsList = projects['projects']  # it's a dic, we need it's list
            prlist = ['%s- %s' % (i['id'], i['name']) for i in projectsList]  # clean list
            self.serverPrList.append(prlist)  # add list to gui


    def serverPrSelectCmd(self, *args):
        '''This command will be executed when something in selected in server PR list'''
        selectedList = self.serverPrList.getSelectItem()
        if selectedList:
            selected = selectedList[0]
            self.serverSeqList.removeAll()  # clean the list
            prid = selected.split('-')[0]
            #print prid
            data = self.getSeqDataFromServer(prid)  # get Seq information about project
            if data:  # if there is any sequence data
                seqList = data['seqs']
                seqList = ['Sequence %s' % i['number'] for i in seqList]
                self.serverSeqList.append(seqList)  # add fresh list
                self.serverSeqList.setEnable()  #  enable selection on list
            #else:  # if there is are no seqs:
                #self.serverSeqList.setDisable()


    def serverSeqSelectCmd(self, *args):
        '''This command will be executed when something in selected in server SEQ list'''
        selectedList = self.serverSeqList.getSelectItem()
        selectedList_pr = self.serverPrList.getSelectItem()
        if selectedList:
            selected = selectedList[0]
            selected_pr = selectedList_pr[0]
            self.serverShotList.removeAll()  # clean the list
            seq = selected.split(' ')[1]
            prid = selected_pr.split('-')[0]
            #print prid
            data = self.getShotDataFromServer(prid, seq)  # get Seq information about project
            if data:  # if there is any sequence data
                shotList = data['shots']
                shotList = ['Shot %s' % i['number'] for i in shotList]
                self.serverShotList.append(shotList)  # add fresh list
                self.serverShotList.setEnable()  #  enable selection on list


    def updateAssignTexts(self, *args):
        '''Update Scene information'''
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

    def getAssignSelections(self):
        ## Get Selections
        selectedPrs = self.serverPrList.getSelectItem()  # get list 
        selectedSeqs = self.serverSeqList.getSelectItem()
        selectedShots = self.serverShotList.getSelectItem()
        selectedPr, selectedSeq, selectedShot = None, None, None
        prname, prid, seqnum, shotnum = None, None, None, None
        if selectedPrs:
            selectedPr = selectedPrs[0]
            prname = selectedPr.split('- ')[-1]
        if selectedSeqs:
            selectedSeq = selectedSeqs[0]
        if selectedShots:
            selectedShot = selectedShots[0]
        prid = selectedPr.split('-')[0]
        seqnum = selectedSeq.split()[1]
        if selectedShot:
            shotnum = selectedShot.split()[1]
        return (prname, prid, seqnum, shotnum)

    def assign(self, *args):
        '''Assign current scene to information of Vixen Server'''
        ## Get Selections
        prname, prid, seqnum, shotnum = self.getAssignSelections()
        if not (prid and seqnum):
            warning('Vixen Error: You must select at least a sequence!')
        else:  # a sequence is selected
            fileInfo(rm='vseq')  #remove previos data
            fileInfo(rm='vshot')
            scenePath = workspace(pp=sceneName())
            if shotnum:
                shotdata = self.getShotUUID(prid, seqnum, shotnum)
                if shotdata:
                    shotuuid = shotdata['shot']
                    fileInfo['vshot'] = shotuuid
                    self.setPathShotOnServer(shotuuid, scenePath)  # update scene path
                    self.assignText.setLabel('Assigned to shot%s-seq%s of %s project' % \
                            (shotnum, seqnum, prname))
                    menulabel = 'Shot%s/Seq%s of %s project' % (shotnum, seqnum, prname)
                    menuItem('vserverInfoMenu', e=1, l=menulabel)
            else: # not any shot selected
                seqdata = self.getSeqUUID(prid, seqnum)
                if seqdata:
                    sequuid = seqdata['seq']
                    fileInfo['vseq'] = sequuid
                    self.setPathSeqOnServer(sequuid, scenePath)  # update scene path
                    self.assignText.setLabel('Assigned to seq%s of %s project' % \
                            (seqnum, prname) )
                    menulabel = 'Seq%s of %s project' % (seqnum, prname)
                    menuItem('vserverInfoMenu', e=1, l=menulabel)

                #self.save()

                    #print 'Assigned to sequence: %s' % sequuid
    def openSceneByInfo(self, *args):
        '''Open scene file based on selection info of assignment panel'''
        prname, prid, seqnum, shotnum = self.getAssignSelections()
        scenePath = self.openBasedOnNumbers(prid, seqnum, shotnum)
        if scenePath:
            print('Opening: "%s"' % scenePath)
            try:
                openFile(scenePath, force=True, iv=1)  # refresh the file
            except RuntimeError:
                warning('Vixen Error: File not found.')
        else:
            warning('Vixen: No file information available on server.')
        #print prname, prid, seqnum, shotnum
        
    def smartSel(self, mode='pr'):
        '''Auto select and refresh'''
        if not frameLayout('Vixen', ex=1):
            return

        self.updateVlist()
        listStr = []
        try:
            listStr = fileInfo['vSel'].split(',')  # Save selection list in file
        except KeyError:
            self.report.append('fileInfo error: no attribute "vSel"')
        if listStr and len(listStr[0]):  # If there is any nodes specified in fileInfo['vSel']:
            try:
                select(listStr)  # Select all listed nodes
            except MayaNodeError:
                pass
    
        ver = int(fileInfo['av'])
        numOfVers = self.vlistSc.getAllItems()
        if self.assetDb and numOfVers and ver and (ver <= numOfVers):
            self.vlistSc.setSelectIndexedItem([ver])
            self.stextc()
            record = self.getRec(ver)
            if record:
                self.setAssetHud(record)
        else:
            self.setHud('')

    def cra(self, *args):
        '''Compress files for better performance'''
        #self.craAnn.setLabel('  Please Wait ...')
        self.getVID()
        if self.assetDb:
            self.execute(self.assetDb, ['gc'], v=True)
        else:
            warning('Vixen: You need to check in before compressing.')
        #self.craAnn.setLabel('  Use this button for performance improvement.')

    def opf(self, *args):
        '''Open project folder'''
        self.getVID()
        if self.assetDb:
            self.explore(self.assetDb)
        else:
            warning('Vixen: You need to check in before browsing project.')

    def arp(self, *args):
        '''Archive project (git repository) as a ZIP archive.'''
        self.getVID()
        if self.assetDb:
            arName = '%s%s%s' % (self.ws, os.path.sep, '%s_Archive' % \
                os.path.basename(self.ws).title())
            self.gitarchive(self.assetDb, fileInfo['av'], arName)
        else:
            warning('Vixen: You need to check in before archiving project.')

    def save(self, *args):
        '''Commit changes for the project'''
        #if frameLayout('Vixen', ex=1):
            #self.vlistSc.deselectAll()  # Deselect every version from list
        self.saveScene()  # first we save the scene file.
        av = fileInfo['av']
        numOB = 'Number of backups : %s' % av
        #self.avT.setLabel(label)
        self.banT.setLabel(numOB)
        desc=textField('DiscriptionField', q=1, text=1)
        self.descriptionText.setLabel(desc)
        desc=textField('DiscriptionField', e=1, text='')
        self.smartSel()
        if int(av):  # if the version on not zero:
            headsUpMessage('Scene check in as version %s' % av, time=1.0)

    def vishWeb(self, *args):
        '''Visit Vishka.com website'''
        link = 'http://www.vishka.com'
        wb.open(link)

    def bugreport(self,  *args):
        '''report bugs'''
        v1, v2, v3 = config.version.split('.')
        #blink = '127.0.0.1:8000'
        blink = 'ourway.ir'
        link = 'http://%s/vixen/home/bugs?v1=%s&v2=%s&v3=%s&os=%s&er=%s' \
            % (blink, v1, v2, v3, os.name, base64.b64encode('|'.join(self.report)))
        wb.open(link)

    def aDragSlider(self, *args):
        version = self.vslider.getValue()
        record = self.db((self.db.git.version == version) & \
            (self.db.git.vID == self.assDb.vID)).select().first()
        if record:
            self.AssVerText.setLabel('Version: %s  [%s]' % \
                (record.version, pd(record.datetime)))
            sThumId = record.thumb  # we got thumbnal file db id
            thmPath = self.genImgFromDb(fileId=sThumId)  # now we generate a tmp image of thumbnal
            self.assetPrImg.setImage(thmPath)  # set Image

    def selectAsset(self, *args):
        '''When we select a file from project list'''
        sel = self.pfileList.getSelectItem()
        if sel:
            sel = sel[0].split()[-1]
            self.assDb = self.db(self.db.asset.id == \
                sel).select().first()
            record = self.db(self.db.git.id == \
                self.assDb.current).select().first()
            max_val = len(self.assDb.history)
            if record:
                #print record
                #print max_val
                if max_val > 1:
                    self.vslider.setMaxValue(max_val)
                    self.vslider.setEnable()
                else:
                    self.vslider.setEnable(False)
                    #for i in dir(self.vslider):print i
                self.vslider.setValue(record.version)
                self.AssVerText.setLabel('Version: %s  [%s]' % \
                    (record.version, pd(record.datetime)))
                sThumId = record.thumb  # we got thumbnal file db id
                thmPath = self.genImgFromDb(fileId=sThumId)  # now we generate a tmp image of thumbnal
                self.assetPrImg.setImage(thmPath)  # set Image
            else:  # record is not available:
                self.AssVerText.setLabel('Not Available!')
                self.vslider.setEnable(False)  # disable slider
                self.assetPrImg.setImage(self.logo)  # set default Image

    def getFname(self, aid, mode='open'):
        '''Get filename of selected asset from project list'''
        assDb = self.db(self.db.asset.id == aid).select().first()
        #print 'target asset is: %s' % assDb
        #print self.wsolist.getValue()
        projectdb = self.db(self.db.project.name == \
            self.wsolist.getValue()).select().first()
        #print projectdb.path
        #for i in dir(self.wsolist):print i
        if mode == 'open':
            self.ws = projectdb.path
            self.setWs(self.ws)  # reset workspace
            #self.ws = projectdb.path  # Update workspace variable
        version = self.vslider.getValue()
        #print 'Vixen:' % assDb
        self.vID = assDb.vID
        file_name = self.gitcheckout(assDb, version)  # restore to previous version
        #print file_name
        #print self.vID
        return file_name

    def fileDg(self):
        '''Open a file dialog and return file pathes as a list'''
        basicFilter = '''
            All files (*.*);;3D files (*.ma *.mb *.obj *.3ds);;
            Documents (*.pdf *.doc *.txt *.log);;
            Images (*.jpg *.tif *.tiff *.tdl *.ptx *.png *.tga *.rgb *.exr)
            '''
        dirtList = fileDialog2(fileFilter=basicFilter, okc='Add to Asset', \
            fm=4, dialogStyle=2, cap= 'Choose Files', rf=1)
        if dirtList:
            data = dirtList[:-1]  # last entry is unusful
            #print data
            return data

    def attach(self, *args):
        flist = self.fileDg()
        newFlist = set()  # only for this method
        #print flist
        if flist:
            for i in flist:
                nfn = self.copyLocal(i, 'data')  # copy to data folder
                #self.filelist.add(nfn)
                newFlist.add(nfn)
                #print nfn

            for i in newFlist:
                name = os.path.basename(i)
                path = workspace(pp=i)
                newEn = self.db.attachs.insert(name=name, path=path, vID=self.vID)
                #print newEn

            os.chdir(self.ws)
            self.gitadd(self.assetDb, newFlist)  # add to repo

            self.db.commit()  # commit changes.
        #print newFlist
        self.updateAttachList()
            
        #return flist
    def updateAttachList(self):
        '''Update attach list in Attach tab.'''
        self.getVID()
        #data = ['asd','Asd']
        #print self.attachments
        data = [f.name for f in self.attachments]
        #for i in self.attachments:
        self.attachList.removeAll()  # clean the list
        if data:
            self.attachList.append(list(set(data)))
        return data

    def openAttach(self, *args):
        '''Open selected attachment file'''
        if self.attachList.getSelectItem():  # If there is a selection
            fname = self.attachList.getSelectItem()[0]
            atdb = self.db( (self.db.attachs.name == fname) & \
                (self.db.attachs.vID == self.vID)).select().first()
            #print 'Opining Attachement: %s' % atdb.path
            self.gitcheckout(self.assetDb, filelist=[atdb.path])
            fpath = '%s%s%s' % (self.ws, os.path.sep, atdb.path)
            return self.openFile(fpath)
    
    def openScene(self, *args):
        '''This function will be run when user doublel cicks on project fileslist.'''

        if self.pfileList.getSelectItem():  # If there is a selection
            aid = self.pfileList.getSelectItem()[0].split()[-1]
            self.setProg(5, 'Reading file information')
            file_name = self.getFname(aid, mode='open')
            self.setProg(9, 'Opening scene file')
            if file_name:  # if file is available:
                openFile(file_name, force=True, iv=1)  # refresh the file
                self.setProg(45, 'Loading new file information')
                self.assetDb = self._getAssetFromDb
                self.setProg(56, 'reloading Textures')
                self.reloadTextures()
                self.setProg(76, 'Refereshing GUI')
                self.smartSel()
                self.setProg(84, 'Selecting objects')
                sver = int(self.vlistSc.getSelectItem()[0].split('.')[0])  # first selection
                self.setProg(90, 'Checking out used files and textures')
                self.gitcheckout(self.assetDb, sver, self.getUsedTxs() )  # restore files
                self.setProg(100, 'Done')
            else:
                warning('Vixen: Error 109 - File is not available!!!')
                

    def getPFiles(self):
        '''get all assets from current project'''
        #for i in dir(self.wsolist):print i
        if self.wsolist.getItemListLong():
            ws = self.wsolist.getValue()
            data = self.db(self.db.asset.workspace == \
                ws).select(orderby=~self.db.asset.id)
            return data
        else:
            return []

    def getProjects(self):
        '''Find all project names and return them'''
        assets = self.db(self.db.asset.workspace).select()
        data = set()
        if assets:
            for i in assets:
                data.add(i.workspace)
        return data

    def getShortName(self, name):
        '''Short a name'''
        try:
            tmp1 = name.split(os.path.sep)[-1].split('.')[0].split('__')[0]
            tmp2 = 'Test_%s' % name.split('.')[-2].split('_')[-1]
            return tmp1 or tmp2
        except IndexError:
            return name

    def getPFString(self, v):
        '''Get a list string base on a asset. v is an asset db'''
        if v and v.name and not v.disabled:
            bname = self.getShortName(v.name)
            if v.label:
                bname = self.getShortName(v.label)
            data = ' %s%s[%s]%s%s' % (bname.lower().capitalize()[:15], \
                ' ' * (15 - len(bname)), len(v.history),\
                ' ' * (4 - len(str(len(v.history)))), v.id)
            return data

    def getPfItems(self):
        items = []
        for v in self.getPFiles():
            data = self.getPFString(v)
            if data:  # TODO
                items.append(data)
        return items

    def addPrMenus(self):
        '''Add projects to list'''
        Prs = self.getProjects()  # Get list of projects
        self.wsolist.clear()
        for item in Prs:
            menuItem(p=self.wsolist, label=item, bld=1)
        wsname = os.path.basename(self.ws)
        if wsname in Prs:  # if current workspace is available in database
            self.wsolist.setValue(wsname)  # set the item to current workspace (project)
        self.updatePfileList()

    def updatePfileList(self, *args):
        '''Update list of project files'''
        self.pfileList.removeAll()  # delete all items first
        self.pfileList.append(self.getPfItems())  # update list
        clistItems = self.pfileList.getAllItems()
        if clistItems:  # if there are any files in project:
            csSt = self.getPFString(self.assetDb)
            if  csSt in clistItems:
                self.pfileList.setSelectItem(csSt)  # select first item
            else:
                self.pfileList.setSelectIndexedItem(1)  # select first item
        #for i in dir(self.pfileList):print i
        self.selectAsset()

    def updateVlist(self):
        '''Update versions list'''
        #print self.assetHistoryDb
        #self.assetHistoryDb = self._getAssetFromDb()
        self.getVID()
        data = ['%s. %s' % (v.version, v.description.title()) \
            for v in self.assetHistoryDb]
        self.vlistSc.removeAll()  # clean the list
        if data:
            self.vlistSc.append(data)
        return data

    def vRefresh(self, *args):
        '''Refresh UI'''
        if frameLayout(self.VWN, ex=1):
            fvID = frameLayout(self.VWN, q=1, dtg=1)  # get dtg of frameLayout
            if fvID != self.vID:
                deleteUI(self.VWN)
                self.vWin()

        #else:
            #Asset()
                #self.vWin() #
            #sys.exit()
        #else:

    def vOpen(self, *args):
        '''Happens when with enable vixen icon'''
        
        if frameLayout('Vixen', io=1, q=1):
            iconTextCheckBox('vIcon', e=1, v=1)
            self.vsb.setVisible(1)
        #self.vAddToSide()

    def vClose(self, *args):
        '''Close Vixen UI'''
        if not frameLayout('Vixen', io=1, q=1):
            iconTextCheckBox('vIcon', e=1, v=0)
            self.vsb.setVisible(0)



    def ftpopen(self, *args):
        '''Open ftp access site'''
        
        loc = 'ftp://%s@localhost:29897/' % self.username
        wb.open(loc)
        warning('Vixen: Open this address in your browser: %s' % loc)

    def embed(self, *args):
        '''Embed everything to scene file'''
        #sm = dgmodified()
        self.saveScene(description='Auto Save')  # first we save scene
        files = self.getUsedFiles()
        count = 0
        for i in files:
            path = '%s/%s' % (self.ws, i)
            state = self.embedImage(path)
            if state:
                count += 1

        self.filelist=set()
        if count:
            self.saveScene(description='Embedded Some Textures')  # first we save scene
        self.smartSel()  # refresh

    def extract(self, *args):
        '''extract images'''
        keys = fileInfo.keys()
        for key in keys:
            if 'vTex_' in key:
                self.extractImage(key)
        
        # explore the folder
        dstpath = '%s/sourceimages/embedded' % self.ws
        if not os.path.isdir(dstpath):
            os.makedirs(dstpath)
        wb.open(dstpath)

    def vRef(self, *args):
        '''refrence selected asset from projects'''
        if self.pfileList.getSelectItem():  # If there is a selection
            aid = self.pfileList.getSelectItem()[0].split()[-1]
            file_name = self.getFname(aid, mode='ref')  # checkout the file
            if file_name:
                cmds.file(file_name, iv=1, r=True, \
                    ns=self.getShortName(file_name).replace(os.path.sep, '_'))

    def vImport(self, *args):
        '''import selected asset to current scene from project list'''
        '''refrence selected asset from projects'''
        if self.pfileList.getSelectItem():  # If there is a selection
            aid = self.pfileList.getSelectItem()[0].split()[-1]
            file_name = self.getFname(aid, mode='import')
            if file_name:
                cmds.file(file_name, i=True, iv=1, \
                    ns=self.getShortName(file_name).replace(os.path.sep, '_'))

    def vAddToSideTop(self, *args):
        '''Add to sidebar'''
        iconTextCheckBox('vIcon', e=1, v=1)
        if frameLayout(self.VWN, ex=1):
            paneLayout('ChannelsLayersPaneLayout', e=1, cn="horizontal3")
            paneLayout('ChannelsLayersPaneLayout', e=1,\
                setPane=(melGlobals['gChannelBoxForm'], 2))
            paneLayout('ChannelsLayersPaneLayout', e=1, setPane=(self.vsb, 1))
        else:
            self.vOpen()  # create ui
            self.vAddToSideTop()  # repat again

    def vAddToSideSingle(self, *args):
        '''Add to sidebar'''
        iconTextCheckBox('vIcon', e=1, v=1)
        if frameLayout(self.VWN, ex=1):
            paneLayout('ChannelsLayersPaneLayout', e=1, cn="single")
            paneLayout('ChannelsLayersPaneLayout', e=1, setPane=(self.vsb, 1))
        else:
            self.vOpen()  # create ui
            self.vAddToSideSingle()  # repat again

    def vAddToSide(self, *args):
        '''Add to sidebar'''
        
        if frameLayout(self.VWN, ex=1):
            paneLayout('ChannelsLayersPaneLayout', e=1, cn="horizontal3")
            paneLayout('ChannelsLayersPaneLayout', e=1,\
                setPane=(melGlobals['gChannelBoxForm'], 1))
            paneLayout('ChannelsLayersPaneLayout', e=1, setPane=(self.vsb, 2))
        else:
            
            self.vOpen()  # create ui
            self.vAddToSide()  # repat again

    def renameScene(self, *args):
        ''' Rename scene'''
        result = promptDialog(
                        title='Rename Scene',
                        message='Enter Name:',
                        button=['OK', 'Cancel'],
                        defaultButton='OK',
                        cancelButton='Cancel',
                        dismissString='Cancel')

        if result == 'OK':
            text = promptDialog(query=True, text=True)
            aPath = self.getAssetProject(self.assetDb).path
            #fileInfo['vName']=text
            scenePath = '%s/%s' % (aPath, self.assetDb.name)
            #print scenePath
            if os.path.isfile(scenePath):
                newpass = scenePath.replace(os.path.basename(scenePath), '%s.mb' % text)
                #print newpass
                os.link(scenePath, newpass)
                newname = self.assetDb.name.replace(os.path.basename(self.assetDb.name), '%s.mb'%text)
                self.assetDb.update_record(name=newname)
                fileInfo['vName'] = text
                self.db.commit()
                #newpass = '%s/%s.mb' % (aPath, text)
                #dirname = os.path.dirname(self.assetDb)
                #if dirname:
                    #newpass = '%s/%s/%s.mb' % (aPath, dirname, text)
                #print newpass   
            #print aPath 

    def label(self, *args):
        ''' Rename scene'''
        sel = self.pfileList.getSelectItem()
        if sel:
            sel = sel[0].split()[-1]
            assDb = self.db(self.db.asset.id == sel).select().first()
            #print assDb
        result = promptDialog(
                        title='Set Label',
                        message='Enter Label:',
                        button=['OK', 'Cancel'],
                        defaultButton='OK',
                        cancelButton='Cancel',
                        dismissString='Cancel')

        if result == 'OK':

            label = promptDialog(query=True, text=True)
            assDb.update_record(label=label)
            self.db.commit()
            self.addPrMenus()

    def updateServerLoc(self, *args):
        '''Update server loc'''
        newLoc = self.serverLocField.getText()
        servdb = self.db(self.db.prefs.name == 'server').select().first()
        servdb.update_record(value=newLoc)
        self.db.commit()
        
        
    def hideAsset(self, *args):
        ''' Rename scene'''
        sel = self.pfileList.getSelectItem()
        if sel:
            sel = sel[0].split()[-1]
            assDb = self.db(self.db.asset.id == sel).select().first()

        if assDb:
            assDb.update_record(disabled=True)
            self.db.commit()
            self.addPrMenus()

    def updateDescription(self, *args):
        ''' Update description'''

    def removeVersion(self, *args):
        ''' Remove Version '''


    def updateIQuenceList(self, *args):
        ''' Update iQuence '''
        self.iQuenceList.removeAll()  # delete all items first
        iQuencePathPref = self.db(self.db.prefs.name=='iQuencePath').select().first()
        if iQuencePathPref:
            path = iQuencePathPref.value
        else:
            path = self.ws
        #print path
        data = self.getIQuence(path)
        #print data
        if data:
            data.sort()
            mylist = ['%s- |%s   [%s-%s]' % (data.index(d)+1,  \
                d['name'][:20], d['start'], \
                d['end']) for d in data]

            self.iQuenceList.append(mylist)  # update list
            clistItems = self.iQuenceList.getAllItems()
            self.iQList = data
        #~ print self.iQList

        
    def playSeq(self, *args):
        '''Play selected iQuence'''
        nukePathPref = self.db(self.db.prefs.name=='nukepath').select().first() 
        if self.iQuenceList.getSelectItem():  # If there is a selection
            sel = self.iQuenceList.getSelectItem()[0]
            playnum = int(sel.split('-')[0]) - 1
            #~ print playnum
            data = self.iQList[playnum]
            cmd = data['fcheck']
            if nukePathPref:
                cmd = data['nuke'].replace('<nukepath>', nukePathPref.value)
            iquence.run_player(cmd)
            
    def mp4Seq(self, *args):
        '''Convert selected sequence to mp4 file format using ffmpeg'''
        if self.iQuenceList.getSelectItem():  # If there is a selection
            sel = self.iQuenceList.getSelectItem()[0]
            playnum = int(sel.split('-')[0]) - 1
            #~ print playnum
            data = self.iQList[playnum]
            cmd = data['seq2mp4']
            sep = os.path.sep
            ffmpegpath = 'ffmpeg'
            if os.name == 'posix':
                ffmpegpath = '%s%sutils%sbin%sffmpeg' % (self.vixenpath, sep, sep, sep)
            elif os.name == 'nt':
                ffmpegpath = '%s%sutils%sbin%sffmpeg.exe' % (self.vixenpath, sep, sep, sep)
            cmd = cmd.replace('<ffmpegpath>', ffmpegpath)
            pr = iquence.Process(cmd)
            pr.start()
    
    def selectNuke(self, *args):
        nukePathPref = self.db(self.db.prefs.name=='nukepath').select().first()
        flist = fileDialog2(fm=1, okc='Select Nuke Executable')
        if flist:
            nukepath = flist[0]
            if not nukePathPref:
                self.db.prefs.insert(name='nukepath', value=nukepath)
            else:
                nukePathPref.update_record(value=nukepath)
            
            self.db.commit()

    def selectiQuenceDir(self, *args):
        iQuencePathPref = self.db(self.db.prefs.name=='iQuencePath').select().first()
        flist = fileDialog2(fm=3, okc='Select as iQuence Path')
        if flist:
            qpath = flist[0]
            if not iQuencePathPref:
                self.db.prefs.insert(name='iQuencePath', value=qpath)
            else:
                iQuencePathPref.update_record(value=qpath)
            
            self.db.commit()
            self.iQuenceList.removeAll()  # delete all items first
            self.iqpathlabel.setLabel(qpath.replace(self.ws, '<PR>'))

    def tmp(self, *args):
        print self.getIQuence(self.ws)

    def print_vAuth(self, *args):
        vAuth = self.get_vAuth()
        warning('Your Auth key is: %s' % vAuth) 

    def vWin(self, *args):
        '''Sidebar'''
        print 'building Vixen frame'
        self.VWN = "Vixen"
        textCOL = (.7, .7, .75)
        Rcolor = (.1, .4, .6)
        _title = '%s - [ %s/ ] - %s %s' % (self.VWN, os.path.basename(self.ws), \
            config.devMode, config.version)

        #self.vClose()  # refresh
        #self.vRefresh()  # refresh
        self.butlines = formLayout(melGlobals['gChannelsLayersForm'], \
            query=1, childArray=1)
        setParent(melGlobals['gChannelsLayersForm'] + "|" + str(self.butlines[0]))
        if not iconTextCheckBox('vIcon', ex=1):  # If icon is not available:
            iconTextCheckBox('vIcon', ann="Vixen Asset Management",\
                height=32, width=32, image1=self.icon, st="iconOnly",\
                ofc=self.vClose, onc=self.vOpen, v=0)

            popupMenu()
            menuItem(label='Channel / Vixen / Layers', radioButton=True, c=self.vAddToSide)
            menuItem(label='Vixen / Channel / Layers', radioButton=False, c=self.vAddToSideTop)
            menuItem(label='Vixen Only', radioButton=False, c=self.vAddToSideSingle)

        else:
            iconTextCheckBox('vIcon', e=1, v=1)  # Enable it's state

        #print self.butlines
        if frameLayout('Vixen', exists=1):
            #fvID = frameLayout('Vixen', q=1, dtg=1)  # get dtg of frameLayout
            #print 'current vID is: %s' % fvID
            #self.vID = self.getVID()
            #if fvID != self.vID:
                #print 'need to delete this window'
                deleteUI('Vixen', lay=1)
            #else:
             #   return
        #else:
            #print 'I can not find any Vixen! build it again'
        self.vsb = frameLayout(self.VWN, p='ChannelsLayersPaneLayout', l=_title, \
                vcc=self.smartSel, dtg=self.vID, li=10)
        separator(style='none')
        columnLayout(co=('left', 10))
        rowLayout('CheckInRowLayout', nc=2, ct2=('left', 'right'),\
            rat=[(1, 'top', 0), (2, 'top', 0)])
        textField('DiscriptionField', ann="Enter a description and press Enter to check in.", \
                w=140, bgc=textCOL, aie=True, ec=self.save)
        button(l='Check IN', c=self.save, ann='Click to Check In', w=150, bgc=(.51, .51, .51))
        setParent('..')  # back to rowLayout
        setParent('..')  # back to columnLayout

        #for i in dir(self.prog): print i
        #=========================================
        frameLayout(lv=0, h=280)
        tabs = tabLayout()  # new tabLayout

        #### SAVE TAB=========================================================
        rowLayout('Save/Restore', nc=2, ct2=('left', 'right'),\
            rat=[(1, 'top', 0), (2, 'top', 0)])
        frameLayout(w=210, l='History Line',  bgc=Rcolor)
        self.banT = text(align='left', label='Number of versions : %s' % \
            len(self.assetHistoryDb))
        #vlist=range(int(fileInfo['av'])+1)
        self.vlistSc = textScrollList('vlistSc', h=150, sc=self.stextc, dcc=self.dctextc, \
            ann="Your Scene's History List. Double click to load.", fn="boldLabelFont",)
        #for i in dir(self.vlistSc):print i

            #self.vlistSc.setIndexSelection(2)
        popupMenu()
        #menuItem(label='Rename Scene', c=self.renameScene)
        #menuItem(label='Update Description', c=self.updateDescription)
        #menuItem(label='Remove Selected Item', c=self.removeVersion)



        button(l='Load', c=self.dctextc, ann='Click to Load')
        setParent('..')  # back to frameLayout
        #paneLayout()
        columnLayout(co=('left', 5), rs=10)
        frameLayout(l='Asset Description', bgc=(.1, .4, .6), bv=0, bs='etchedOut')
        self.thumbImage = image(image=self.logo, w=150, h=125)
        setParent('..')
        self.descriptionText = text(ww=True, l='')
        self.hisDate = text(ww=True, l='')
        # update and select
        #self.updateVlist()
        self.smartSel(mode='v')


        #####================ Projects ==================================
        with tabs:
            columnLayout('Project', co=('left', 5), rs=0, adj=1)
            rowLayout(nc=2, rat=[(1, 'top', 0), (2, 'top', 0)])
            frameLayout(w=210, l='Project Files', bgc=(.5, .5, .5))
            self.pfileList = textScrollList(h=150, dcc=self.openScene, \
                sc=self.selectAsset, fn="fixedWidthFont", nr=3)
            popupMenu()
            menuItem(label='Set a label', c=self.label)
            menuItem(label='Hide selected asset', c=self.hideAsset)
        #menuItem(label='Update Description', c=self.updateDescription)
        #menuItem(label='Remove Selected Item', c=self.removeVersion)
            rowLayout(nc=3)
            button(l='Open', c=self.openScene, w=100)
            button(l='Import', c=self.vImport)
            button(l='Reference', c=self.vRef)
            setParent('..')
            setParent('..')
            columnLayout(co=('left', 5), rs=10)
            frameLayout(l='Preview', bgc=Rcolor)
            self.assetPrImg = image(image=self.logo, w=150, h=125)
            setParent('..')

            self.vslider = intSlider(w=150, min=1, max=3, value=1, step=1, en=0, dc=self.aDragSlider)
            self.AssVerText = text(l='')
            setParent('..')
            setParent('..')
            columnLayout()
            self.wsolist = optionMenu(w=100, cc=self.updatePfileList)

            self.addPrMenus()

        #### ==== Attach ============
        with tabs:
            #rowLayout('Attach', bgc=(.21, .21, .21))
            columnLayout('Attach', co=('left', 20), rs=10)
            separator()
            rowLayout( nc=2, rat=[(1, 'top', 0), (2, 'top', 0)])
            button(l='Attach Files', c=self.attach )
            text('')
            #self.craAnn = text(l='          Archive everything as a single .Zip archive.')
            setParent('..')
            self.attachList = textScrollList(w=420, h=150, dcc=self.openAttach, nr=3)
            self.updateAttachList()
        #============== iQuence ========================================
        with tabs:
            #rowLayout('Attach', bgc=(.21, .21, .21))
            columnLayout('iQuence', co=('left', 20), rs=10)
            separator()
            #rowLayout( nc=2, rat=[(1, 'top', 0), (2, 'top', 0)])
            #button(l='Attach Files', c=self.attach )
            #~ text('List images sequences of /images directory' )
            #self.craAnn = text(l='          Archive everything as a single .Zip archive.')
            #setParent('..')
            rowLayout( nc=3, rat=[(1, 'top', 0), (2, 'top', 0), (3, 'top', 0)])
            #~ button(l='Refresh Sequence List', c=self.updateIQuenceList)
            iconTextButton( style='iconOnly', ann='Refresh/Update list', image1='refresh.png', c=self.updateIQuenceList )
            iconTextButton( style='iconOnly', ann='Select Nuke executable file for playback', image1='FilmGateDown.png', c=self.selectNuke )
            iconTextButton( style='iconOnly', ann='Update iQuence search directory', image1='SP_DirOpenIcon.png', c=self.selectiQuenceDir)
            setParent('..')
            iQuencePathPref = self.db(self.db.prefs.name=='iQuencePath').select().first()
            pathlabel = 'Search Path: %s' % self.ws
            if iQuencePathPref:
                pathlabel = iQuencePathPref.value
            #~ self.iqpathlabel = text(l=pathlabel)

            pathlabel = pathlabel.replace(self.ws, '<PR>')
            self.iqpathlabel = iconTextButton( en=0, style='iconAndTextHorizontal', image1='SP_FileDialogInfoView.png', l=pathlabel )
            self.iQuenceList = textScrollList(fn="fixedWidthFont", w=420, h=150, dcc=self.playSeq, nr=3)
            #self.updateIQuenceList()
            

            rowLayout( nc=2, rat=[(1, 'top', 0), (2, 'top', 0)])
            #~ button(l='Play Selected', c=self.playSeq)
            iconTextButton( style='iconOnly', w=24, h=24, image1='interactivePlayback.png', ann="Play Selected Sequence", c=self.playSeq )
            iconTextButton( style='iconOnly', ann='Convert to MP4' ,image1='menuIconRenderSettings.png', c=self.mp4Seq )
            #~ button(l='Convert Selected to MP4', c=self.mp4Seq)
            setParent('..')
            
            nukePathPref = self.db(self.db.prefs.name=='nukepath').select().first()
            if nukePathPref and nukePathPref.value and os.path.isfile(nukePathPref.value):
                text('Player: Nuke' )
            else:
                text('*Player: FCheck - Please choose your nuke path' )

        #=============== Tools ======================================
        with tabs:
            columnLayout('Tools', co=('left', 20), rs=10)
            text(l='')
            rowLayout(nc=2)
            button(l='Compress Archive', c=self.cra)
            self.craAnn = text(l='     Use this button for performance improvement.')
            setParent('..')

            rowLayout(nc=2)
            button(l='Open Project Folder', c=self.opf)
            self.craAnn = text(l='  Explore Asset Project Folder')
            setParent('..')
            
            rowLayout(nc=2)
            button(l='Archive Project', c=self.arp)
            self.craAnn = text(l='          Archive everything as a single .Zip archive.')
            setParent('..')
            
            rowLayout(nc=2)
            button(l='Your FTP Area', c=self.ftpopen)
            self.craAnn = text(l='  FTP Access')
            setParent('..')


            rowLayout(nc=2)
            button(l='Embed Textures', c=self.embed)
            self.craAnn = text(l='  Add textures to scene file')
            setParent('..')

            rowLayout(nc=2)
            button(l='Extract Textures', c=self.extract)
            self.craAnn = text(l='  Extract Embedded textures to project')
            setParent('..')

            columnLayout(co=('left', 10))
            text(l='')
            text(l='Execute a custom command on your repository:')
            rowLayout(nc=3)
            text(l='command:')
            self.actext = textField(ec=self.rac, aie=True)
            button(l='Run', c=self.rac)
            setParent('..')
            text('')
            text('Latest Vixen executed command:')
            self.lastEC = textField(w=250, ed=False, bgc=(.5, .5, .5))
        #=============== Servert ======================================
        with tabs:
            columnLayout('Server', co=('left', 20), rs=10, adj=True)
            columnLayout()

        #~ #=============== About ======================================
        #~ with tabs:
            #~ columnLayout('About', adj=True)
            #~ columnLayout()
            #~ #image(image=self.logo, w=150, h=125)
            #~ setParent('..')
            #~ text(l="\nVIXEN for Autodesk Maya")
            #~ text(l='Version %s %s \n' % (config.devMode, config.version))
            #~ text(l='Developed by: Farsheed Ashouri\n')
            #~ text(l='Special Thanks to: \nAlireza ShahramFar and Amin Zarouni')
            #~ text(l='-' * 48)
            #~ ##~ rowLayout(nc=2)
            #~ ##~ self.craAnn = text(l='  Help improving Vixen by sending bug reports')
            rowLayout(nc=4)
            text(l='Server Location: ')
            server = self.db(self.db.prefs.name == 'server').select().first().value
            self.serverLocField = textField(w=250, text=server)
            button(l='Update', c=self.updateServerLoc)
            button(l='A', c=self.print_vAuth)
            setParent('..')
            separator()
            frameLayout(w=420, l='Scene Assignment Panel', bgc=(.1, .4, .6))
            rowLayout(nc=3)
            self.serverPrList = textScrollList(fn="fixedWidthFont", w=140, \
                    h=150, nr=3, sc=self.serverPrSelectCmd)
            self.serverSeqList = textScrollList(fn="fixedWidthFont", en=0, \
                    w=140, h=150, nr=3, sc=self.serverSeqSelectCmd, dcc=self.openSceneByInfo)
            self.serverShotList = textScrollList(fn="fixedWidthFont", en=0, \
                    w=140, h=150, nr=3, dcc=self.openSceneByInfo)
            setParent('..')

            rowLayout(nc=3)
            iconTextButton( style='iconOnly', ann='Refresh/Update list', \
                    image1='refresh.png', c=self.updateAssignProjects )
            button(l='Assign', c=self.assign)
            self.assignText = text(l='')
            setParent('..')
        #Add to sidebar:
        self.vAddToSide()
        self.vClose()
        #timer = Timer(60, self.after)
        #timer.start()
    def show(self):
        self.createMenu()
        self.vWin()
        self.smartSel()

    def createMenu(self):

        mMainMenu = melGlobals.initVar('string', 'gMainWindow')
        if menu('vixenMainWindowMenu', exists=1):
            deleteUI('vixenMainWindowMenu')
        if melGlobals['gMainWindow'] != "":
            setParent(melGlobals['gMainWindow'])
            menu('vixenMainWindowMenu', tearOff=True, label="Vixen")
            menuItem('vserverInfoMenu', label='-- Not Assigned --', \
                    p='vixenMainWindowMenu', c=self.openServerPage)
            menuItem(label='Send Preview to Server', c=self.sendPr, p='vixenMainWindowMenu')
            menuItem(label='Watch Latest Preview', c=self.watchPreview, p='vixenMainWindowMenu')
            menuItem(divider=1, p='vixenMainWindowMenu')
            menuItem(label='Switch to latest version', \
                c=self.stash, p='vixenMainWindowMenu')
            menuItem(label='Explore workspace', \
                c=self.opf, p='vixenMainWindowMenu')
            menuItem(divider=1, p='vixenMainWindowMenu')
            menuItem(label='Report a bug', c=self.bugreport, p='vixenMainWindowMenu')
            menuItem(label='Documentation', c=self.docs, p='vixenMainWindowMenu')
            menuItem(label='Website', c=self.website, p='vixenMainWindowMenu')
            #evalDeferred(add_menus)
            self.updateVserverInfoMenu()  # update aggignment
            self.add_menus()

    def add_menus(self):
        '''Add newded menus'''
        mel.eval('buildFileMenu();')
        fmname = melGlobals['$gMainFileMenu']
        fmenu = [i for i in lsUI(m=1) if i=='MayaWindow|mainFileMenu'][0]
        #print fmenu
        if menu(fmenu, ex=1):
            if not menuItem('vexfile', ex=1):
                vexplorer = menuItem('vexfile', label='Vixen Explorer',  p=fmenu, \
                    stp='python', ia='openFileOptions', c=self.vexplorer)
            if not menuItem('vcheckfile', ex=1):
                vcheck = menuItem('vcheckfile', label='CheckIn (Save Scene)', p=fmenu, ia='saveOptions', c=self.save)

    def watchPreview(self, *args):
        '''Watch latest preview of scene on server'''
        vseq, vshot = self.getVserverInfo()
        server = self.db(self.db.prefs.name == 'server').select().first().value
        data = None
        if vshot:
            data = self.getShotInfoFromUUID(vshot)
        elif vseq:
            data = self.getSeqInfoFromUUID(vseq)

        if data:
            vname = data['preview']
            link = 'home/video?vname=%s' % vname
            url = '%s/%s' % (server, link)
            wb.open(url)

    def updateVserverInfoMenu(self, *args):
        '''Update Scene information'''
        vseq, vshot = self.getVserverInfo()
        label = None
        if vshot:
            data = self.getShotInfoFromUUID(vshot)
            label = 'Shot%s/Seq%s of %s project' % (data['number'], data['seq'], data['pr'])
        elif vseq:
            data = self.getSeqInfoFromUUID(vseq)
            label = 'Seq%s of %s project' % (data['number'], data['pr'])

        if label:    
            menuItem('vserverInfoMenu', e=1, l=label)


    def openServerPage(self, *args):
        '''Open vixen server page of current scene'''
        server = self.db(self.db.prefs.name == 'server').select().first().value
        vseq, vshot = self.getVserverInfo()
        link = None
        if vshot:
            link='home/shotview?shid=%s' % vshot
        elif vseq:
            link='home/sqview?sid=%s' % vseq
        
        if link:
            url = '%s/%s' % (server, link)
            wb.open(url)

    def stash(self, *args):
        '''git stash to latest'''
        warning('Vixen" Not implemented yet.')

    def website(self, *args):
        link = 'http://vixen.alwaysdata.net'
        wb.open(link)

    def docs(self, *args):
        link = 'http://vixen.alwaysdata.net/vixen/home/docs'
        wb.open(link)

    def vexplorer(self, *args):
        '''Vixen Explorer'''
        self.vexp = window('vexplorer', title='Vixen Scene Explorer', w=800, h=400)
        form = formLayout(numberOfDivisions=100)
        b1 = frameLayout(lv=0)
        setParent('..')
        b2 = cmds.button('Open')
        column = cmds.columnLayout()
        button('Not finished! Wait')
        button('B2')
        button(l='B1')

        formLayout(form, edit=True,
                attachForm=[(b1, 'top', 15), (b1, 'left', 5), (b2, 'left', 5), \
                        (b2, 'bottom', 5), (b2, 'right', 5), (column, 'top', 5),\
                        (column, 'right', 5) ],
                attachControl=[(b1, 'bottom', 5, b2), (column, 'bottom', 5, b2)],
                attachPosition=[(b1, 'right', 5, 75), (column, 'left', 0, 75)], 
                attachNone=(b2, 'top') )

        showWindow(self.vexp)
