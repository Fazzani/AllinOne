#-------------------------------------------------------------------------------
# Name:        utils
# Purpose:
#
# Author:      922261
#
# Created:     22/01/2014
# Copyright:   (c) 922261 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import logging
import functools
import time
from bs4 import BeautifulSoup
import urllib, urllib2
import re
import sys
from SearcherABC import Media

#-------------------------------------------------------------------------------
# Name:        utils
# Purpose:
#
# Author:      922261
#
# Created:     22/01/2014
# Copyright:   (c) 922261 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import logging
import functools
import time
from bs4 import BeautifulSoup
import urllib, urllib2
import re
import sys
from SearcherABC import Media


def timed(level=None, format='%s: %s ms'):
    if level is None:
        level = logging.DEBUG
    def decorator(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            logger.addHandler(handler)

            start = time.time()
            result = fn(*args, **kwargs)
            duration = time.time() - start
            logger.log(level, format, repr(fn), duration * 1000)
            return result
        return inner
    return decorator


def tryGetValue(obj, prop="text"):
    try:
      return getattr(obj, prop, '').encode('utf-8').strip()
    except:
      return ""

def getContentOfUrl(url, data = None):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    if data:
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        return response.read()
    content = opener.open(url)
    return content.read()

def GetContentPage(url, page="acceuil"):
    response = getContentOfUrl(url)
    response = response.replace("<sc'+'ript",'<script>')
    response= response.replace("</sc'+'ript>",'</script>')

    tab=[]
    if None != response and 0 < len(response):
        soup = BeautifulSoup(response)
        if page =='details':
            for node in soup.findAll("object"):
                link = node.param["value"]
                print 'node.param["value"] : ' + node.param["value"]
##                if "http://www" not in link and  "http://embed" not in link:
##                    link = link.replace("http://","http://www.")
                tab.append((node.parent.parent.p.img['alt'].encode('utf-8').strip(), link))
            for node in soup.findAll("iframe", width="600"):
                link = node["src"]
##                if "http://www" not in link and  "http://embed" not in link:
##                    link = link.replace("http://","http://www.")
                tab.append((node.parent.parent.parent.p.img['alt'].encode('utf-8').strip(), link))
        else:
            nodes = soup.findAll("div", "post")
            for node in nodes:
                listp = node.find("div","content").findAll("p")
                #returns title, link, img, synopsis
                tab.append(Media(node.h2.a.text.encode('utf-8').strip(), node.h2.a["href"].encode('utf-8').strip(), listp[1].text.encode('utf-8').strip(), listp[0].img["src"]))
        return tab

def GetDomain(url):
        tmp = re.compile('//(.+?)/').findall(url)
        domain = 'Unknown'
        if len(tmp) > 0 :
            domain = tmp[0].replace('www.', '')
        return domain

def GetMediaInfoFromJson(json, typeMedia="tvseries"):
    serie = json[typeMedia]
    media = Media(serie["title"], "", serie["synopsisShort"], serie["poster"]["href"])
    media.Genre= serie["genre"][0]['$']
    media.Year= serie["yearStart"]
    media.Country= serie["nationality"][0]['$']
    media.Cast= serie["castingShort"]['actors']
    return media



def timed(level=None, format='%s: %s ms'):
    if level is None:
        level = logging.DEBUG
    def decorator(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            logger.addHandler(handler)

            start = time.time()
            result = fn(*args, **kwargs)
            duration = time.time() - start
            logger.log(level, format, repr(fn), duration * 1000)
            return result
        return inner
    return decorator


def tryGetValue(obj, prop="text"):
    try:
      return getattr(obj, prop, '').encode('utf-8').strip()
    except:
      return ""

def tryGetValueFromArray(obj, prop):
    try:
      return obj[prop]
    except:
      return ""

def GetContentSearchPage(url):
    response = getContentOfUrl(url)
    response= response.replace("</sc'+'ript>",'</script>')

    tab=[]
    if None != response and 0 < len(response):
        soup = BeautifulSoup(response)
        nextPage = soup.find("a", "nextpostslink")
        if nextPage != None :
            nextPage = nextPage["href"]
        nodes = soup.findAll("div", "post")
        for node in nodes:
            #returns title, link
            tab.append((node.h2.a.text.encode('utf-8').strip(), node.h2.a["href"].encode('utf-8').strip()))
    return (tab, nextPage)

def GetDomain(url):
        tmp = re.compile('//(.+?)/').findall(url)
        domain = 'Unknown'
        if len(tmp) > 0 :
            domain = tmp[0].replace('www.', '')
        return domain

def GetMediaInfoFromJson(json, typeMedia="tvseries"):
    serie = json[typeMedia]
    print repr(serie)
    media = Media(tryGetValueFromArray(serie,"title"), "", tryGetValueFromArray(serie,"synopsisShort"), tryGetValueFromArray(serie,"poster")["href"])
    media.Genre= tryGetValueFromArray(serie, "genre")[0]['$']
    if typeMedia=="tvseries":
        media.Year= tryGetValueFromArray(serie, "yearStart")
    else:
        media.Year= tryGetValueFromArray(serie, "productionYear")

    media.Country= tryGetValueFromArray(serie, "nationality")[0]['$']
    media.Cast= tryGetValueFromArray(tryGetValueFromArray(serie, "castingShort"), 'actors')
    media.Director= tryGetValueFromArray(tryGetValueFromArray(serie, "castingShort"),'directors')
    return media


