#-*- coding: utf-8 -*-
import sys
import xbmc
import xbmcvfs
import xbmcaddon
import utils
import time
from datetime import datetime
import re

__addon__ = xbmcaddon.Addon(id='plugin.service.allinone')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
__last_run__ = 0
__sleep_time__ = 5000


def readLastRun():
  global __last_run__ 
  if(__last_run__ == 0):
  #read it in from the settings
    __last_run__ = float(utils.getSetting('last_run'))

def writeLastRun():
  global __last_run__ 
  utils.setSetting('last_run',str(__last_run__))

def go():
    global __last_run__ 
    if(xbmc.Player().isPlaying() == False):
        utils.showNotification('Start Update TeleduNet','Mise a jour de la playlist...')
        #recuperer la page du Site
        url = 'http://www.teledunet.com/'
        htmlContent = utils.makeRequest(url)
        #chercher l'id
        index = htmlContent.index("id0=") + 4
        newedId = htmlContent[index:index + 13].replace('.','') + '00'
        print ("the new Id of Télédunet.com :::::::::::::::::::::::::::: %s" % newedId)
        #maj de la playlist de la LiveTv
        __datapath__ = xbmc.translatePath("smb://192.168.1.254/Disque\040dur/XBMC/myplaylist2.m3u").decode('utf-8')
        if xbmcvfs.exists(__datapath__):
            file = xbmcvfs.File(__datapath__,'r+')
            contentfile = file.read()
            index = contentfile.index("id0=") + 4
            oldId = contentfile[index:index + 14]
            contentfile = contentfile.replace(oldId, newedId)
            file.close()
            f = xbmcvfs.File(__datapath__, 'w')
            f.seek(0, 0);
            result = f.write(contentfile)
            f.close()

        #Enregistrement du dernier passage
        __last_run__ = time.time()
        writeLastRun()
        xbmc.executebuiltin('StartPVRManager')


while (not xbmc.abortRequested):
  delaySettings = __addon__.getSetting("delay")
  readLastRun()
  delay = 3600 * int(delaySettings)
  #don't check unless new minute
  if(time.time() > __last_run__ + (delay)):
      go()
      
  xbmc.sleep(__sleep_time__)