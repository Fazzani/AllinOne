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

class Streamzzz(SearcherABC.SearcherABC):

    tab =["(Date de sortie)(.*?)$", "(Année de production)(.*?)$","(Nom du film)(.*?)$", "(Réalisé par)(.*?)$","(Avec)(.*?)$","(Genre)(.*?)$","(Durée)(.*?)$","(Nationalité)(.*?)$"]
    api = Allocine()

    def __init__(self):
        self.api.configure('100043982026','29d185d98c984a359e6e6f26a0474269')

    BASE_URL = "http://streamzzz.com"

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
    searchIcon = '/resources/searchers/icons/logoOmg.png'

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
        #http://streamzzz.com/search/dead/next/1
        url = "%s/search/%s/next/1" % (self.BASE_URL, (urllib.quote_plus(keyword)))
        res = self.GetContentSearchPage(url)
        infoMedia = Media()
        if len(res[0]) > 0 :
            search = self.api.search(keyword, "tvseries")
            if int(search['feed']['totalResults']) > 0 :
                infoMedia = Utils.GetMediaInfoFromJson(self.api.tvseries(search['feed']['tvseries'][0]['code'],"small"))

        for (title, link) in res[0]:
            search = self.api.search(keyword, "tvseries")
            if infoMedia :
                 filesList.append((
                    title,
                    link,
                    infoMedia,
                    self.__class__.__name__,
                ))
            else:
                filesList.append((
                    title,
                    link,
                    None,
                    self.__class__.__name__,
                ))
               
        return filesList

    def GetContentSearchPage(self, url):
        response = Utils.getContentOfUrl(url).replace('scr"+"ipt','script')
        tab=[]
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
            
            nextPage = soup.find("a", "pagination-next")
            if nextPage != None :
                nextPage = nextPage["href"]
            nodes = soup.findAll('ul','search-res')[1].findAll("li")
            for node in nodes:
                #returns title, link
                tab.append((node.h3.a.text.encode('utf-8').strip(), node.h3.a["href"].encode('utf-8').strip()))
        return (tab, nextPage)

    '''
    Get Info Media from Url
    '''
    def getInfoMediaFromUrl(self, medialink):
        if((re.search(r"/films/", medialink, re.M|re.I)==None) and (re.search(r"/series/", medialink, re.M|re.I)==None)):
            return None

        return self.extractInfosMedia(self.makeRequest(medialink))

    '''
    Extract infos Media from html content page
    '''
    def extractInfosMedia(self, htmlContent):
        media = Media()
        if None != htmlContent and 0 < len(htmlContent):
            soup = BeautifulSoup(htmlContent)
            ficheFilmBloc = soup.find("div", {"class" : "page_content"})
            fiche = ficheFilmBloc.findAll("li")

            for f in fiche:
                li = f.text.encode('utf-8').strip()

                if re.match(self.tab[0], li):
                    media.ReleaseDate = re.match(self.tab[0], li).group(2)
                elif re.match(self.tab[1], li):
                    media.Year = re.match(self.tab[1], li).group(2)
                elif re.match(self.tab[2],li):
                    media.Title = re.match(self.tab[2],li).group(2)
                elif re.match(self.tab[3],li):
                    media.Director = re.match(self.tab[3],li).group(2)
                elif re.match(self.tab[4], li):
                    media.Cast = re.match(self.tab[4], li).group(2)
                elif re.match(self.tab[5], li):
                    media.Genre = re.match(self.tab[5], li).group(2)
                elif re.match(self.tab[6], li):
                    media.Duration = re.match(self.tab[6], li).group(2)
                elif re.match(self.tab[7], li):
                    media.Country = re.match(self.tab[7], li).group(2)

            media.PictureLink = re.sub(r"/r_([0-9]+)_([0-9]+)/","/r_1090_600/", ficheFilmBloc.findAll("img", "film_img")[0]["src"])
            media.Plot = tryGetValue(ficheFilmBloc.findAll("div", recursive=False)[1].p)
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
                    tab.append(Media(node.h2.a.text, node.h2.a["href"].encode('utf-8').strip(), listp[1].text.encode('utf-8').strip(), listp[0].img["src"]).__dict__)
        return tab