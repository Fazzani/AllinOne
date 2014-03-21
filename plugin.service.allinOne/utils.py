#-*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import cookielib
import urllib2
 
__addon_id__= 'plugin.service.allinone'
__Addon = xbmcaddon.Addon(__addon_id__)

def data_dir():
    return __Addon.getAddonInfo('profile')

def addon_dir():
    return __Addon.getAddonInfo('path')

def log(message,loglevel=xbmc.LOGNOTICE):
    xbmc.log(encode(__addon_id__ + ": " + message),level=loglevel)

def showNotification(title,message):
    xbmc.executebuiltin("Notification(" + encode(title) + "," + encode(message) + ",2000," + xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/images/clock.png") + ")")

def setSetting(name,value):
    __Addon.setSetting(name,value)

def getSetting(name):
    return __Addon.getSetting(name)
    
def getString(string_id):
    return __Addon.getLocalizedString(string_id)

def encode(string):
    return string.encode('UTF-8','replace')

def makeRequest(url, data={}, headers=[]):
    cookieJar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3; rv:28.0) Gecko/20100101 Firefox/28.0'),('Referer', 'http://www.google.fr'),('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
    if 0 < len(data):
        encodedData = urllib.urlencode(data)
    else:
        encodedData = None
    return opener.open(url, encodedData).read()
