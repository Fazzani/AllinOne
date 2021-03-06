#-*- coding: utf-8 -*-
import sys
import xbmc
import xbmcvfs
import xbmcaddon
import utils
import time
from datetime import datetime
import re
import urlparse

__addon__ = xbmcaddon.Addon(id='plugin.service.allinone')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
__last_run__ = 0
__sleep_time__ = 5000
__DefaultPathOfPlayList__ = "smb://192.168.1.254/Disque\040dur/XBMC/myplaylist2.m3u"
__delaySettings__=60
__force__= False

def getNewId(url, pattern, offset):
    htmlContent = utils.makeRequest(url)
    index = htmlContent.index(pattern) + len(pattern)
    return htmlContent[index:index + offset]

def getNewContent(contentfile, pattern, offset, newedId):
    index = contentfile.index(pattern) + len(pattern)
    oldId = contentfile[index:index + offset]
    return contentfile.replace(oldId, newedId)

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
        utils.showNotification('Start Update','Mise a jour de la playlist...')
        #recuperer la page du Site
        newedId = getNewId('http://www.teledunet.com/','id0=',13).replace('.','') + '00'
        while('E' in newedId):
            print("pass in boucle because this id %s contain E" % newedId)
            newedId = getNewId('http://www.teledunet.com/','id0=',13).replace('.','') + '00'

        newedIdLiveTv = getNewId('http://www.livetv.tn/','code=w_', 15)
        #print("the new Id of télédunet :::::::::::::::::::::::::::: %s" %
        #newedId)
        #print("the new Id of livetv.tn :::::::::::::::::::::::::::: %s" %
        #newedIdLiveTv)
        #maj de la playlist de la LiveTv
        __datapath__ = xbmc.translatePath(__PathOfPlayList__).decode('utf-8')
        #__datapath__ =
        #r"C:\Users\922261\Desktop\myplaylist2.m3u".decode('utf-8')
        if xbmcvfs.exists(__datapath__):
            file = xbmcvfs.File(__datapath__,'r+')
            contentfile = file.read()
            #Màj Télédunet
            contentfile = getNewContent(contentfile, "id0=", 14, newedId)
            #Màj Live Tv
            contentfile = getNewContent(contentfile, "code=w_", 15, newedIdLiveTv)
            
            file.close()
            f = xbmcvfs.File(__datapath__, 'w')
            f.seek(0, 0)
            result = f.write(contentfile)
            f.close()

        #Enregistrement du dernier passage
        __last_run__ = time.time()
        writeLastRun()
        xbmc.executebuiltin('StartPVRManager')

if __name__ == '__main__':
    #print('________________________________')
    #print (repr(sys.argv))
    if(len(sys.argv)>1):
        args = urlparse.parse_qs(sys.argv[1])
        #print(args["mode"][0])
    if(len(sys.argv)>1 and args["mode"][0]=='true') :
        #print('--------------------------')
        __force__= True
    __delaySettings__ = __addon__.getSetting("delay")
    __PathOfPlayList__ = __addon__.getSetting("path_input")
    if(__PathOfPlayList__== "" ):
      __PathOfPlayList__ = __DefaultPathOfPlayList__

while (not xbmc.abortRequested):
  readLastRun()
  delay = 3600 * int(__delaySettings__)
  #delay = 60
  #don't check unless new minute
  if((time.time() > __last_run__ + (delay)) or __force__):
      try:
        go()
      except:
        print "Unexpected error:", sys.exc_info()[0]
      __force__ = False
      
  xbmc.sleep(__sleep_time__)

#http://localhost:2000/jsonrpc?request={'jsonrpc:'2.0','id':1,'method':'Addons.ExecuteAddon','params':{'addonid':'plugin.service.allinone','params':{'mode':'true'}}}
