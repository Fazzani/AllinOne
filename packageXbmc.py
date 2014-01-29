#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      922261
#
# Created:     27/01/2014
# Copyright:   (c) 922261 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import zipfile
import os
import sys

def getSettings(path):
    tab=[]
    file=open(path, 'r')
    for ligne in file:
         tab.append(ligne.rstrip('\n').split('='))
    print tab
    return tab

def zipdir(path, zip, settings):

    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[-1].lower() not in str(settings[0][1]).split(__sepExt__):
                zip.write(os.path.join(root, file))

def main():

    settings = getSettings(__SettingsFilePath__)
    zipFileName= __current_dir__ + settings[3][1]
    zipFileName=r"C:\Users\Heni\Documents\GitHub\AllinOne\AllinOne\Addons\plugin.video.allinonetest\plugin.video.allinonetest-1.0.0.zip"
    zipf = zipfile.ZipFile(zipFileName, 'w')
    zipdir(settings[2][1], zipf, settings)
    zipf.close()
    execfile(__current_dir__+ settings[4][1])
    pass

__SettingsFilePath__='settings.txt'
__sepExt__=";"
__current_dir__= os.path.dirname(sys.argv[0])

if __name__ == '__main__':
    main()
