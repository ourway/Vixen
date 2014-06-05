#!/usr/bin/env mayapy

#Vixen licensing module
#By: Farsheed Ashouri
#copyright: Vishka Studio, www.Vishka.com

'''
Vishka END-USER LICENSE AGREEMENT FOR ViXEN

IMPORTANT PLEASE READ THE TERMS AND CONDITIONS OF THIS LICENSE AGREEMENT CAREFULLY BEFORE CONTINUING WITH THIS PROGRAM INSTALL:

Vishka End-User License Agreement ("EULA") is a legal agreement between you (either an individual or a single entity) and Vishka. for the Vishka Vixen(s) identified above which may include associated software components, media, printed materials, and "online" or electronic documentation Vixen. By installing, copying, or otherwise using the Vixen, you agree to be bound by the terms of this EULA. This license agreement represents the entire agreement concerning the program between you and Vishka, (referred to as "licenser"), and it supersedes any prior proposal, representation, or understanding between the parties. If you do not agree to the terms of this EULA, do not install or use the Vixen.

The Vixen is protected by copyright laws and international copyright treaties, as well as other intellectual property laws and treaties. The Vixen is licensed, not sold.

1. GRANT OF LICENSE.
The Vixen is licensed as follows:
(a) Installation and Use.
Vishka grants you the right to install and use copies of the Vixen on your computer running a validly licensed copy of the operating system for which the Vixen was designed [e.g., Windows 95, Windows NT, Windows 98, Windows 2000, Windows 2003, Windows XP, Windows ME, Windows Vista, All Unix based Operating Systems including Mac, Ubuntu, Redhat or Slackware.].
(b) Backup Copies.
You may also make copies of the Vixen as may be necessary for backup and archival purposes.

2. DESCRIPTION OF OTHER RIGHTS AND LIMITATIONS.
(a) Maintenance of Copyright Notices.
You must not remove or alter any copyright notices on any and all copies of the Vixen.
(b) Distribution.
You may not distribute registered copies of the Vixen to third parties. Evaluation versions available for download from Vishka's websites may be freely distributed.
(c) Prohibition on Reverse Engineering, Decompilation, and Disassembly.
You may not reverse engineer, decompile, or disassemble the Vixen, except and only to the extent that such activity is expressly permitted by applicable law notwithstanding this limitation.
(d) Rental.
You may not rent, lease, or lend the Vixen.
(e) Support Services.
Vishka may provide you with support services related to the Vixen. Any supplemental software code provided to you as part of the Support Services shall be considered part of the Vixen and subject to the terms and conditions of this EULA.
(f) Compliance with Applicable Laws.
You must comply with all applicable laws regarding use of the Vixen.

3. TERMINATION
Without prejudice to any other rights, Vishka may terminate this EULA if you fail to comply with the terms and conditions of this EULA. In such event, you must destroy all copies of the Vixen in your possession.

4. COPYRIGHT
All title, including but not limited to copyrights, in and to the Vixen and any copies thereof are owned by Vishka or its suppliers. All title and intellectual property rights in and to the content which may be accessed through use of the Vixen is the property of the respective content owner and may be protected by applicable copyright or other intellectual property laws and treaties. This EULA grants you no rights to use such content. All rights not expressly granted are reserved by Vishka.

5. NO WARRANTIES
Vishka expressly disclaims any warranty for the Vixen. The Vixen is provided 'As Is' without any express or implied warranty of any kind, including but not limited to any warranties of merchantability, noninfringement, or fitness of a particular purpose. Vishka does not warrant or assume responsibility for the accuracy or completeness of any information, text, graphics, links or other items contained within the Vixen. Vishka makes no warranties respecting any harm that may be caused by the transmission of a computer virus, worm, time bomb, logic bomb, or other such computer program. Vishka further expressly disclaims any warranty or representation to Authorized Users or to any third party.

6. LIMITATION OF LIABILITY
In no event shall Vishka be liable for any damages (including, without limitation, lost profits, business interruption, or lost information) rising out of 'Authorized Users' use of or inability to use the Vixen, even if Vishka has been advised of the possibility of such damages. In no event will Vishka be liable for loss of data or for indirect, special, incidental, consequential (including lost profit), or other damages based in contract, tort or otherwise. Vishka shall have no liability with respect to the content of the Vixen or any part thereof, including but not limited to errors or omissions contained therein, libel, infringements of rights of publicity, privacy, trademark rights, business interruption, personal injury, loss of privacy, moral rights or the disclosure of confidential information.
'''

import os
import re
import ctypes
import hashlib
import config
import sys
import getpass
import datetime
import cPickle as pickle
from base64 import b64decode
try:
    from pymel.all import *
except ImportError:
    pass
reload(config)


class License(object):
    '''Vixen License Utils'''

    def __init__(self):
        '''constructor'''
        self.hostId = self.getHostId()

     
    def getHostId(self):
        """Get the hardware address on Windows by running ipconfig.exe."""
        #dirs = ['', r'c:\windows\system32', r'c:\winnt\system32', r'd:\windows\system32']
        try:
            buffer = ctypes.create_string_buffer(300)
            ctypes.windll.kernel32.GetSystemDirectoryA(buffer, 300)
            dirs.insert(0, buffer.value.decode('mbcs'))
        except:
            pass
        if os.name == 'nt':
            #for dir in dirs:
            pipe = os.popen('ipconfig /all')
            #print pipei
            #TODO

            for line in pipe:
                value = line.split(':')[-1].strip().lower()
                if re.match('([0-9a-f][0-9a-f]-){5}[0-9a-f][0-9a-f]', value):
                    whid = value.replace('-', '')         # return a string that is host id.  justTypr: gethostId()
                    return whid
        elif os.name == 'posix':
                pipe = os.popen('ifconfig')
                for line in pipe:
                    try:
                        value = line.split()[-1].strip()
                        if re.match('([0-9a-f][0-9a-f]:){5}[0-9a-f]', value):
                            lhid = value.replace(':', '')
                            return lhid
                    except IndexError:
                        pass
                    #value = line.split(':')[-1].strip().lower()
                    #print value

    def linGen(self, hid):
        '''Generate a license based on a given host id'''
        Cvar = 'There%sIsNo%sGreaterBore%sThanPrefection%s' % (hid[:2], hid[2:4], hid[4:6], hid[6:8])
        lic = hashlib.sha512(Cvar).hexdigest()
        return lic

    def getDiffDay(self, dt):
        '''Return diffrence day of today and the given datetime'''
        evoDay = dt.timetuple().tm_yday  # example 125
        today = datetime.datetime.now().timetuple().tm_yday  # example 180
        if today < evoDay:
            today += 365
        diffDay = today - evoDay
        return diffDay

    def evo(self):
        '''Prepare for evolution'''
        sep = os.path.sep
        if sys.platform == 'win32':
            var = 'APPDATA'
        elif sys.platform == 'linux2':
            var = 'HOME'
        else:
            warning('Vixen Error: Your platform is not supported yet.')
            sys.exit()
        varEnv = os.getenv(var)  # get the environment variable of var
        self.evoPath = '%s%s.vixen' % (varEnv, sep)
        if not os.path.isdir(self.evoPath):  # is not available:
            os.makedirs(self.evoPath)  # create that path
        self.evoFile = '%s%s.evo' % (self.evoPath, sep)
        return self.evoFile

    def doEvo(self):
        '''Generate evo lic'''
        if os.path.isfile(self.evo()):  # If evo file is available:
            dt = pickle.load(open(self.evoFile, "rb"))
            diff = self.getDiffDay(dt)
            #print diff
            if diff >= 0 and diff < 365:
                return True
        else:  # We must create new evo file
            dtnow = datetime.datetime.now()  # Start evo date
            pickle.dump(dtnow, open(self.evoFile, "wb"))

            self.doEvo()  # Run method again

    def chkLicense(self):
        #print linGen(getHostId())
        #self.evo() #prepareations
        sep = os.path.sep
        licPath = '%s%slicense%svishka.lic' % (config.getpath(), sep, sep)
        self.lic = False
        if os.path.isfile(licPath):  # license file is available
            ldatalines = open(licPath, 'r').readlines()  # read first line of code
            if ldatalines:
                ldata = ldatalines[0]
                if ldata == self.linGen(self.getHostId()):  # Check License file
                    self.lic = True
                    return self.lic
        else:  # lic file is not available
            rem = self.doEvo()
            #print rem
            if rem:
                self.lic = True
                print('Vixen: You are in non-commercial mode.')
                return self.lic

        if not self.lic:
            warning('Vishka License is not available. Your HostID is: [%s]. visit: www.VISHKA.com/Vixen for more information.' % self.getHostId())
            #return False
            sys.exit()  # finish program.


if __name__ == '__main__':
    vsp = getpass.getpass('Enter Vixen Super Password: ')
    vspds = 'Q2NfMTgzMDYw'
    if vsp == b64decode(vspds):
        hid = raw_input('HostId: ')
        #ldu = raw_input('License Expiration Limit (Month): ')
        lic = License().linGen(hid)
        open('vishka.lic', 'w').write(lic)
        print 'License file: vishka.lic created.'
