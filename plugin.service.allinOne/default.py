#-*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon
import utils
import time
from datetime import datetime
import re

__addon__ = xbmcaddon.Addon()
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
        print('____________________run')
        #recuperer la page du Site
        url = 'http://www.teledunet.com/'
        htmlContent = utils.makeRequest(url)
        #chercher l'id
        index = htmlContent.index("id0=") + 4
        print htmlContent[index:index + 13].replace('.','') + '00'
        #maj de la playlist de la LiveTv
        #Enregistrement du dernier passage
        #write last run time
        __last_run__ = time.time()
        writeLastRun()

while (not xbmc.abortRequested):
  
  readLastRun()

  #don't check unless new minute
  if(time.time() > __last_run__ + (3600*24)):
      go()
      
  xbmc.sleep(__sleep_time__)

