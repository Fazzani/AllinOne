#-*- coding: utf-8 -*-
'''
    Torrenter plugin for XBMC
    Copyright (C) 2012 Vadim Skorba
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
from bs4 import BeautifulSoup
import SearcherABC
from SearcherABC import Media
import urllib
import re
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
import Utils
from allocine.Allocine import Allocine

from Utils import timed, tryGetValue

class Smartorrent(SearcherABC.SearcherABC):

    api = Allocine()
    cat= (('tvserie',33),('dvd-rip',11))
    def __init__(self):
        self.api.configure('100043982026','29d185d98c984a359e6e6f26a0474269')

    BASE_URL = "http://smartorrent.com"

    '''
    Weight of source with this searcher provided.
    Will be multiplied on default weight.
    Default weight is seeds number
    '''
    sourceWeight = 1

    '''
    Relative (from root directory of plugin) path to image
    will shown as source image at result listing
    '''
    searchIcon = 'http://files.smartorrent.com/v4/css/../images/logo.gif.png'

    '''
    Flag indicates is this source - magnet links source or not.
    Used for filtration of sources in case of old library (setting selected).
    Old libraries won't to convert magnet as torrent file to the storage
    '''
    @property
    def isMagnetLinkSource(self):
        return False

    '''
    Main method should be implemented for search process.
    Receives keyword and have to return dictionary of proper tuples:
    filesList.append((
        int(weight),# Calculated global weight of sources
        int(seeds),# Seeds count
        str(title),# Title will be shown
        str(link),# Link to the torrent/magnet
        str(image),# Path/URL to image shown at the list
    ))
    '''
    @timed()
    def search(self, keyword):

        filesList = []
        #http://www.smartorrent.com/index.php?page=search&term=dexter&cat=&voir=2
        url = "%s/index.php?page=search&term=%s&cat=&voir=1" % (self.BASE_URL, (urllib.quote_plus(keyword)))
        response = self.makeRequest(url)
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
            nodes = soup.find('table','homelisting').tbody.findAll("tr")
            image = sys.modules["__main__"].__root__ + self.searchIcon

            #print response
            for node in nodes:
                seeds = node.find('td','seed').text.encode('utf-8').strip()
                leechers = node.find('td','leech').text.encode('utf-8').strip()
                titleTorrent = node.find('td','nom').a.find_next().text.encode('utf-8').strip()
                medialink = node.find('td','nom').a.find_next()['href'].encode('utf-8').strip()
                size = node.find('td','taille').text.encode('utf-8').strip()

                torrentTitle = "%s [S\L: (%s\%s) %s]" % (titleTorrent, seeds, leechers, size)
                match = re.match(r'(?:.+?)/([0-9]+)/', medialink)
                if match :
                    link = self.BASE_URL + "/?page=download&tid=%s" % match.group(1).encode('utf-8').strip()
                else:
                    return []

                filesList.append(
                    (int(int(self.sourceWeight) * int(seeds)),
                    int(seeds),
                    self.__class__.__name__ + '::' + link,
                    self.getInfoMediaFromUrl,
                    medialink,
                    ))
        return filesList

    def GetContentSearchPage(self, url):
        response = Utils.getContentOfUrl(url)
        tab=[]
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
            nextPage = soup.find("div", {'id':'pagination'}).find('a','actualpage').findNext('a')
            if nextPage != None and 'lastpage' not in nextPage.attrs['class']:
                nextPage = nextPage["href"]
            nodes = soup.find('table','homelisting').findAll("td",'nom')
            for node in nodes:
                #returns title, link
                tab.append((node.a.findNext('a').text.encode('utf-8').strip(), node.a.findNext('a')["href"].encode('utf-8').strip()))
        return (tab, nextPage)

    '''
    Get Info Media from Url
    '''
    def getInfoMediaFromUrl(self, medialink):
        return self.extractInfosMedia(self.makeRequest(medialink))

    '''
    Extract infos Media from html content page
    '''
    def extractInfosMedia(self, htmlContent):
        media = Media()
        if None != htmlContent and 0 < len(htmlContent):
            soup = BeautifulSoup(htmlContent)
            ficheFilmBloc = soup.find("table", "fichetorrent")
            tr = ficheFilmBloc.tbody.findAll("tr")
            media.Title = tr[0].td.nextSibling.h1.string.encode('utf-8').strip()
            media.PictureLink = self.BASE_URL+ tr[0].td.img['src'].encode('utf-8').strip()
            #media.ReleaseDate = f.td.text.encode('utf-8').strip()
            #media.Year = f.td.text.encode('utf-8').strip()
            #media.Title = f.td.text.encode('utf-8').strip()
            #media.Director = f.td.text.encode('utf-8').strip()
            #media.Cast = f.td.text.encode('utf-8').strip()
            #media.Genre = f.td.text.encode('utf-8').strip()
            #media.Duration = f.td.text.encode('utf-8').strip()
            #media.Country = f.td.text.encode('utf-8').strip()
            #media.Plot = tryGetValue(ficheFilmBloc.findAll("div", description),'text')
            return media
        else:
            return media

    def GetPageDetails(self, url="", page="acceuil"):
        if url and url is not None:
            url = urllib.unquote_plus(url)
        else:
            url = urllib.unquote_plus(self.BASE_URL)

        response = Utils.getContentOfUrl(url).replace('sc"+"ript','script').replace("sc'+'ript","script").replace('scr"+"ipt','script').replace("scr'+'ipt","script")
        tab=[]
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
            if page =='details':
                for node in soup.findAll("object"):
                    link = node.param["value"]
                    tab.append((node.parent.parent.p.img['alt'].encode('utf-8').strip(), link))
                for node in soup.findAll("iframe", width="600"):
                    link = node["src"]
                    tab.append((soup.find('div','page_content').p.text.encode('utf-8').strip(), link))
            else:
                nodes = soup.findAll("div", "post")
                for node in nodes:
                    listp = node.find("div","content").findAll("p")
                    tab.append(Media(node.h2.a.text, node.h2.a["href"].encode('utf-8').strip(), listp[1].text.encode('utf-8').strip(), listp[0].img["src"]))
        return tab