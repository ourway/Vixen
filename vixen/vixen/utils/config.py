#!/usr/bin/env mayapy

#part of Vixen Asset managemet system
#Copyrigh: Vishka Studio, Tehran, Iran
#Author: Farsheed Ashouri
version = '0.9.5'
devMode = 'Beta'
import base64
import os
import sys

logoEncode = '''
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
'''

iconEncode = '''
iVBORw0KGgoAAAANSUhEUgAAACAAAAAPCAYAAACFgM0XAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A
/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9wEHAobAZXBRskAAAJ/SURBVDjL
7ZRLbIxRGIaf9///aY3owUJC3C0al2EigtqIDRuJBHuJhERMJaIdVSFBXKKdDhaIlbWFRFgLCQvV
hKpbXRYSSoS4/GlQM3M+C6JiZlq3pTf5Nud87/ee73bET4ibUyFoMui1y/X08w8QN8+bAzxyuZ7P
P98FZd5RspYwsQG4EO9sqP978fR6pKsEwYRK91HZiS8GmE0GllH42Bk3z8tT+HDMHXsc/5bwttlL
CRIHEA1mFimMRlfyUxmxae44pEdIgwSzT0idSGcpFTspFfvc0d6+75zMlAQ1dfVEUT1mS0BrEdPB
9F3Cl3Zilnf5uwNVHxBn59aCdn21IWD2zTxIg1aez4+kd8BCmPrYtV8on4F4W0p4GkAtw9ZXgiCA
MIIgBAXDiANoDEYe/2RkWQXibDoAWoBdmCUxewl6iKweafzwwatWyjDrQjJgPlBjWJfCxDqFUW/d
wesozqbnA+cxm4T0FGmVa+vuBuhvWyX/9sVEKwyskZQBhtkKA1TC+zOE4WlqRlx1+699Aug/vDLh
Xz09ZNAoqRazk5hlFGfTAk5gtglfPOfy91ZXWaexmO1AbP/a70r6vhfzm13H3UsVYzTOSDNi1BUk
j/fLMesKXPstw5cyYBnCxKJ489SgEtnlbr0lkdyD1IjZm/LMuYjC1dXEAUjWLQOe4P0spC6XvzPY
3LgpFSCtQOFi1969d8gdz6Y3Aqcw07ehvIiCLa7t5v2qnNaF4ygMtGI+hy89d0ful6/hu8w0KUyM
VbJupDt841nVYFtnJolqdiO1YvYAs02u4/bloR79vimVAh6M7rhTGPIj+uWfrmXBRHxxH2Y3XK7n
OP/xh/gCtuH2wkuMMnwAAAAASUVORK5CYII=
'''


def logo(path):
    '''Generate Logo'''
    logodata = base64.decodestring(logoEncode)
    logoFile = open(path, 'wb')
    logoFile.write(logodata)
    logoFile.close()


def icon(path):
    '''Generate icon'''
    icondata = base64.decodestring(iconEncode)
    iconFile = open(path, 'wb')
    iconFile.write(icondata)
    iconFile.close()




def getpath(storage=1):
    '''Add some costum pathes to sys.path.'''        
    sep = os.path.sep
    if sys.platform == 'win32':
        var = 'APPDATA'
    elif sys.platform == 'linux2':
        var = 'HOME'
    else:
        print('Vixen Error: Your platform is not supported yet.')
        sys.exit()
    varEnv = os.getenv(var)  # get the environment variable of var
    if storage:
        path = '%s%s.vixen' % (varEnv, sep)
    else:
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isdir(path):  # is not available:
        os.makedirs(path)  # create that path
    os.chdir(path)

    if not path in sys.path:
        sys.path.append(path)
    mpath = '%s%sutils' % (path, os.path.sep)
    if not mpath in sys.path:
        sys.path.append(mpath)
    return path

#path = add_paths()


if __name__ == '__main__':
    '''We will test things here'''
    logo('test.png')
