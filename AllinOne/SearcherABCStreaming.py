#-*- coding: utf-8 -*-
'''
    Torrenter plugin for XBMC
    Copyright (C) 2012 Fazzani Heni
    tunisienheni@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import abc
import urllib
import urllib2
import cookielib
import re
import tempfile
import hashlib
import xbmcgui
import xbmc
import Localization
import sys
import Utils
from allocine.Allocine import Allocine
from Media import Media
from bs4 import BeautifulSoup

class SearcherABCStreaming:
    __metaclass__ = abc.ABCMeta
    __cache__ = sys.modules["__main__"].__cache__
    api = Allocine()

    def __init__(self):
        self.api.configure('100043982026','29d185d98c984a359e6e6f26a0474269')
        try:
            import StorageServer
        except:
            import storageserverdummy as StorageServer
        self.__cache__ = StorageServer.StorageServer((sys.argv[0]), 1) # (Your plugin name, Cache time in hours)


    searchIcon = '/icons/video.png'
    cookieJar = None

    @abc.abstractmethod
    def search(self, keyword, page = 1):
        return

    @abc.abstractproperty
    def BASE_URL(self):
        return 'Should never see this'
    
    nextPage = ""

    '''
    Le type de contenu du site
    les films et les séries la valeur par défaut
    '''
    @property
    def contentType(self):
        return ContentType.MovieAndTvSerie

    def makeRequest(self, url, data={}, headers=[]):
        self.cookieJar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
        opener.addheaders = headers
        if 0 < len(data):
            encodedData = urllib.urlencode(data)
        else:
            encodedData = None
        return opener.open(url, encodedData).read()

    def askCaptcha(self, url):
        urllib.URLopener().retrieve(url, tempfile.gettempdir() + '/captcha.png')
        window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        image = xbmcgui.ControlImage(460, 20, 360, 160, tempfile.gettempdir() + '/captcha.png')
        window.addControl(image)
        keyboardCaptcha = xbmc.Keyboard('', Localization.localize('Input symbols from CAPTCHA image:'))
        keyboardCaptcha.doModal()
        captchaText = keyboardCaptcha.getText()
        window.removeControl(image)
        if not captchaText:
            return False
        else:
            return captchaText

    htmlCodes = (('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#39;'),)
    stripPairs = (('<p>', '\n'),
        ('<li>', '\n'),
        ('<br>', '\n'),
        ('<.+?>', ' '),
        ('</.+?>', ' '),
        ('&nbsp;', ' '),)

    def unescape(self, string):
        for (symbol, code) in self.htmlCodes:
            string = re.sub(code, symbol, string)
        return string

    def stripHtml(self, string):
        for (html, replacement) in self.stripPairs:
            string = re.sub(html, replacement, string)
        return string

    def md5(self, string):
        hasher = hashlib.md5()
        hasher.update(string)
        return hasher.hexdigest()

    def GetContentFromUrl(self, url=None, data=None):
        if url and url is not None:
            url = urllib.unquote_plus(url)
        else:
            url = urllib.unquote_plus(self.BASE_URL())

        return Utils.getContentOfUrl(url, data).replace("<sc'+'ript",'<script>').replace("<scr'+'ipt",'<script>').replace("</scr'+'ipt",'</script>').replace('</scr"+"ipt','</script>').replace('<scr"+"ipt','<script>').replace("</sc'+'ript>",'</script>')

    @abc.abstractmethod
    def LatestMovies(self, url):
        pass

    @abc.abstractmethod
    def AllTvSeries(self):
        pass

    @abc.abstractmethod
    def LatestTvSeriesEpisodes(self, url):
        pass

    '''
    Fill Media(TvSérie) object from AlloCiné
    '''
    def FillMediaTvSerieFromScraper(self, title, link='', plot='', pic=''):
        infoMedia = Media(title, link, plot, pic)
        #TODO : à virer 
        #return infoMedia
        try:
            search = self.__cache__.cacheFunction(self.api.search, title, "tvseries")
            if int(search['feed']['totalResults']) > 0 :
                return Utils.GetMediaInfoFromJson(self.__cache__.cacheFunction(self.api.tvseries, search['feed']['tvseries'][0]['code'],"small"))
        except:
            return infoMedia
        return infoMedia

class ContentType:
    TvSerieOnly, MoviesOnly, MovieAndTvSerie = range(3)
