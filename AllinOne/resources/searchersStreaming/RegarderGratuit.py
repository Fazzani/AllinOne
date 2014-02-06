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
from bs4 import BeautifulSoup
import SearcherABCStreaming
from Media import Media
import urllib
import re
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
import Utils
from allocine.Allocine import Allocine

from Utils import timed, tryGetValue

class RegarderGratuit(SearcherABCStreaming.SearcherABCStreaming):

    tab =["(Date de sortie)(.*?)$", "(Année de production)(.*?)$","(Nom du film)(.*?)$", "(Réalisé par)(.*?)$","(Avec)(.*?)$","(Genre)(.*?)$","(Durée)(.*?)$","(Nationalité)(.*?)$"]
    api = Allocine()

    def __init__(self):
        self.api.configure('100043982026','29d185d98c984a359e6e6f26a0474269')

    def BASE_URL(self):
        return "http://www.regarder-film-gratuit.com"

    nextPage=""
    
    '''
    Relative (from root directory of plugin) path to image
    will shown as source image at result listing
    '''
    searchIcon = '/resources/searchers/icons/logoOmg.png'

    @property
    def contentType(self):
        return ContentType.TvSerieOnly   

    @timed()
    def search(self, keyword):

        filesList = []
        url = "%s/page/1/?s=%s" % (self.BASE_URL(), (urllib.quote_plus(keyword)))
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
            ficheFilmBloc = soup.find("div", {"class" : "infos_fiche"})
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

    def GetContentSearchPage(self, url):
        response = Utils.getContentOfUrl(url)
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

    '''
    @returns title, link, synopsis, img
    '''
    def GetPageDetails(self, url="", page="acceuil"):
        response= self.GetContentFromUrl(url)
        tab=[]
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
            if page =='details':
                for node in soup.findAll("object"):
                    link = node.param["value"]
                    tab.append((node.parent.parent.p.img['alt'].encode('utf-8').strip(), link))
                for node in soup.findAll("iframe", width="600"):
                    link = node["src"]
                    tab.append((node.parent.parent.parent.p.img['alt'].encode('utf-8').strip(), link))
            else:
                nodes = soup.findAll("div", "post")
                self.nextPage = soup.find('div',{'id':'pagenavi'}).findChild('a','nextpostslink')['href']
                print(self.nextPage)
                for node in nodes:
                    listp = node.find("div","content").findAll("p")
                    #returns title, link, synopsis, img
                    tab.append(node.h2.a.text, 
                               node.h2.a["href"].encode('utf-8').strip(),
                               Media(node.h2.a.text, node.h2.a["href"].encode('utf-8').strip(), listp[1].text.encode('utf-8').strip(), listp[0].img["src"]).__dict__,
                               self.__class__.__name__)
        return tab

    def LatestMovies(self, url):
        return []
    '''
    @returns title, link, synopsis, img
    '''
    def AllTvSeries(self):
        response = self.GetContentFromUrl()
        tab=[]
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
            nodes = soup.find("div", {"id" : "categories-3"}).li.ul.findAll('li')
            for node in nodes:
                tab.append((node.a.text.encode('utf-8'),
                           node.a["href"].encode('utf-8').strip(),
                           Media(node.a.text.encode('utf-8'), node.a["href"].encode('utf-8').strip(), node.a["title"], "").__dict__,
                           self.__class__.__name__))
        return tab

    '''
    @returns title, link, synopsis, img
    '''
    def LatestTvSeriesEpisodes(self, url):
        response= self.GetContentFromUrl(url)
        tab=[]
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
            nodes = soup.findAll("div", "post")
            self.nextPage = soup.find('div',{'id':'pagenavi'}).findChild('a','nextpostslink')['href']
            print(self.nextPage)
            for node in nodes:
                listp = node.find("div","content").findAll("p")
                tab.append((node.h2.a.text,
                           node.h2.a["href"].encode('utf-8').strip(),
                           Media(node.h2.a.text, node.h2.a["href"].encode('utf-8').strip(), listp[1].text.encode('utf-8').strip(), listp[0].img["src"]).__dict__,
                           self.__class__.__name__))
        return tab