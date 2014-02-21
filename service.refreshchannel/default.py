#-*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
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

def go(pathOfPlayList):
    utils.showNotification('Start Update','Mise a jour de la playlist...')
    pb = xbmcgui.DialogProgress()
    pb.create('Refresh', 'Refresh de la PlayList en cours')
    pb.update(0)
    #recuperer la page du Site
    newedId = getNewId('http://www.teledunet.com/','id0=',13).replace('.','') + '00'
    while('E' in newedId):
        print("pass in boucle because this id %s contain E" % newedId)
        newedId = getNewId('http://www.teledunet.com/','id0=',13).replace('.','') + '00'
    pb.update(20)
    newedIdLiveTv = getNewId('http://www.livetv.tn/','code=w_', 15)
    #maj de la playlist de la LiveTv
    datapath = xbmc.translatePath(pathOfPlayList).decode('utf-8')
    pb.update(40)

    #r"C:\Users\922261\Desktop\myplaylist2.m3u".decode('utf-8')
    try:
        if xbmcvfs.exists(datapath):
            file = xbmcvfs.File(datapath,'r+')
            contentfile = file.read()  
            #Màj Télédunet
            contentfile = getNewContent(contentfile, "id0=", 14, newedId)
            #Màj Live Tv
            contentfile = getNewContent(contentfile, "code=w_", 15, newedIdLiveTv)
            file.close()
            pb.update(60)
            f = xbmcvfs.File(datapath, 'w')
            f.seek(0, 0)
            result = f.write(contentfile)
            f.close()
            pb.update(80)
            xbmc.executebuiltin('StartPVRManager')
    except:
        pass
    pb.update(100)
    pb.close()

if __name__ == '__main__' and not xbmc.Player().isPlaying():
    xbmc.executebuiltin("XBMC.ActivateWindow(10000)")
    pathM3u = __addon__.getSetting("path_input")
    if(pathM3u == "" ):
      pathM3u = __DefaultPathOfPlayList__
    try:
        go(pathM3u)
        xbmc.sleep(20000)
    except:
        xbmc.log("Unexpected error: %s" % sys.exc_info()[0], level = xbmc.LOGDEBUG)
xbmc.executebuiltin("XBMC.ActivateWindow(10601)")