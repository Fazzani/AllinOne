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

__DefaultPathOfPlayList__ = "smb://192.168.1.254/Disque\040dur/XBMC/myplaylist2.m3u"

def getNewId(url, pattern, offset):
    htmlContent = utils.makeRequest(url)
    index = htmlContent.index(pattern) + len(pattern)
    return htmlContent[index:index + offset]

def getNewContent(contentfile, pattern, offset, newedId):
    index = contentfile.index(pattern) + len(pattern)
    oldId = contentfile[index:index + offset]
    return contentfile.replace(oldId, newedId)

def go():
    if(xbmc.Player().isPlaying() == False):
        utils.showNotification('Start Update','Mise a jour de la playlist...')
        #recuperer la page du Site
        newedId = getNewId('http://www.teledunet.com/','id0=',13).replace('.','') + '00'
        while('E' in newedId):
            print("pass in boucle because this id %s contain E" % newedId)
            newedId = getNewId('http://www.teledunet.com/','id0=',13).replace('.','') + '00'

        newedIdLiveTv = getNewId('http://www.livetv.tn/','code=w_', 15)
       
        __datapath__ = xbmc.translatePath(__PathOfPlayList__).decode('utf-8')
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
        xbmc.executebuiltin('StartPVRManager')

if __name__ == '__main__':
    #print('________________________________')
    __PathOfPlayList__ = __addon__.getSetting("path_input")
    if(__PathOfPlayList__== "" ):
      __PathOfPlayList__ = __DefaultPathOfPlayList__
    go()
