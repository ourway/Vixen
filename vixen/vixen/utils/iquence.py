#! /usr/bin/python

import os
import fnmatch
from subprocess import Popen, PIPE, call  # everything nedded to handle external commands
import threading
from walkdir import filtered_walk, dir_paths, all_paths, file_paths

class Process(threading.Thread):
    '''Run ftp server'''
    def __init__(self, execfn):
        threading.Thread.__init__(self)
        self.execfn = execfn
        print 'Vixen: iQuence - Starting %s ...' % self.getName() 

    def run(self):
        '''General external process'''
        p = Popen(self.execfn, shell=True, env=os.environ, stdout=PIPE, universal_newlines=True)  # process
        (stdout, stderr) = p.communicate()
        #print execfn
        #~ p.wait()
        print stderr
        return stdout


def run_player(cmd):
    '''execute a command in threading mode'''
    pr = Process(cmd)
    data = pr.start()
    return data


#~ def walklevel(some_dir, level=1):
    #~ '''limit os.walk '''
    #~ some_dir = some_dir.rstrip(os.path.sep)
    #~ assert os.path.isdir(some_dir)
    #~ num_sep = some_dir.count(os.path.sep)
    #~ for root, dirs, files in os.walk(some_dir, followlinks=True):
        #~ yield root, dirs, files
        #~ num_sep_this = root.count(os.path.sep)
        #~ if num_sep + level <= num_sep_this:
            #~ del dirs[:]



class iQuence(object):
    '''The main sequencer class'''
    def __init__(self, topdir, depth=1, *args, **kw):
        '''constructor'''
        self.topdir = topdir
        self.depth = depth
        
        

    def padFrame(self, frame,pad):
        return '0' * (pad - len(str(frame))) + str(frame)

    #~ def find_files(self, pattern):
        #~ '''Find files based on a pattern'''
        #~ self.all_files = set()
        #~ pattern = '*.*.%s' % pattern
        #~ for path, dirname, filelist in walklevel(self.topdir):
            #~ for name in filelist:
                #~ if fnmatch.fnmatch(name, pattern):
                    #~ relpath = os.path.join(path, name)
                    #~ #fullpath = os.path.abspath(relpath)
                    #~ self.all_files.add(relpath)  #now we have all files in a set

        #~ print self.all_files
        #~ return self.all_files
    
    def extractDict(self, fileset):
        '''Extract diffrent base names'''
        result = {}
        for image in fileset:
            details = image.split('.')
            prefix = '.'.join(details[:-2])
            frame = details[-2]
            suffix = details[-1]
            name = '%s.%s' % (prefix, suffix)
            try:
                try:
                    int(frame)
                    result[name].append(frame)
                except ValueError:
                    pass
            except KeyError:
                result[name]=[frame]
                #~ pass
        #~ print result
        return result

    def parseDict(self, fileDict):
        '''Parse dictionary of files
            fcheck -n <start> <end> <step> image.#.rla
            note that # is a shortcut for @@@@
        '''
        sortedList = set()
        for prefix in fileDict:
            frames = fileDict[prefix]
            frames.sort()
            #~ print frames
            int_frames = [int(frame) for frame in frames]
            int_frames.sort()
            startFrame = int_frames[0]
            endFrame   = int_frames[-1]
            pad = len(frames[0])
            idealRange = set(range(startFrame, endFrame))
            realFrames = set([int(x) for x in frames])
            #~ print idealRange
            #~ # sets can't be sorted, so cast to a list here
            missingFrames = list(idealRange - realFrames)
            missingFrames.sort()
            
            #calculate fancy ranges
            #~ subRanges = []  # clean new range
            #~ for gap in missingFrames:
                #~ if startFrame != gap:
                    #~ rangeStart = self.padFrame(startFrame,pad)
                    #~ rangeEnd  = self.padFrame(gap-1,pad)
                    #~ subRanges.append([rangeStart, rangeEnd])
                #~ startFrame = gap+1

            #~ subRanges.append('-'.join([self.padFrame(startFrame,pad), self.padFrame(endFrame,pad) ]))
            #~ frameRanges = ','.join(subRanges)
            #~ suffix = result[prefix][1]
            #~ sortedList.append((prefix, frameRanges))
        #~ else: sortedList.append(prefix)
            #~ print startFrame
            seqname = '%s.#.%s' % ('.'.join(prefix.split('.')[:-1]), prefix.split('.')[-1])
            seqpath = os.path.abspath(seqname)
            sortedList.add((seqpath, startFrame, endFrame, pad, len(missingFrames)))
        #~ print sortedList
        return sortedList

    def genViewerCmds(self, data):
        '''
        Generate fcheck, nuke, shake, ... commands dict
        
        example output:
        {'room_Fa_Ma_12.9.12_b5e.Table_render_cam.#.png': {'fcheck': 'fcheck -n 1 200 1 /home/farsheed/maya/projects/Domjombonakha/images/room_Fa_Ma_12.9.12_b5e.Table_render_cam.@.png'}}
        
        '''
        result=[]
        for i in data:
            cmdsdict = {}
            seqpath = os.path.abspath(i[0])
            start = i[1]
            end = i[2]
            pad = i[3]
            missing = i[4]
            fcheckcmd = 'fcheck -n %s %s 1 %s' % (start, end, \
                seqpath.replace('#', '@'*pad))
            
            nuke_std_path = seqpath.replace('#', '%'+ '0%dd' % pad)
            ffplaycmd = 'ffplay %s' % (nuke_std_path)
            seq2mp4cmd = '<ffmpegpath> -sameq -y -i %s %s.mp4' % (nuke_std_path, seqpath.replace('#','convert'))
            nukecmd = '<nukepath> -v -F %s-%s %s' % (start, end, nuke_std_path)
            cmdsdict['fcheck'] = fcheckcmd
            cmdsdict['ffplay'] = ffplaycmd
            cmdsdict['seq2mp4'] = seq2mp4cmd
            cmdsdict['nuke'] = nukecmd
            cmdsdict['name'] = os.path.basename(seqpath)
            cmdsdict['start'] = start
            cmdsdict['end'] = end
            cmdsdict['pad'] = pad
            cmdsdict['missing'] = missing
            result.append(cmdsdict)
        
        return result
            

    def sequence(self, formats):
        '''return final list'''
        total = []
        print 'iQuence Searching Path: %s' % self.topdir
        fileset = file_paths(filtered_walk(self.topdir, depth=self.depth ,included_files=formats))
        #~ print files
        #for i in fileset: print i
        #~ for pattern in formats:
            #~ fileset = self.find_files(pattern)
        seqDict = self.extractDict(fileset)
        print seqDict
        seqlist = self.parseDict(seqDict)
        #~ print seqlist
            #~ total+=seqlist
            
        cmds = self.genViewerCmds(seqlist)
        #~ print cmds
        return cmds
        

if __name__ == '__main__':
    main = iQuence('/home/farsheed/Projects/Active/Shahrdari/prodoction/Shahrdari_MP/images', depth=1)
    #~ print main
    data = main.sequence(['*.png', '*.tif', '*.exr'])
    print data
    #~ files = file_paths(filtered_walk('/home/farsheed/maya', depth=3,included_files=['*.py', '*.png', '*.rst']))
    #~ print '\n'.join(files)
    #~ for i in files: print i
    #print data['png'][2]['name']
