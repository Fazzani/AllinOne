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
import SearcherABCStreaming
from Media import Media
import urllib
import re
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
import Utils
from Utils import timed, tryGetValue

class Streamay(SearcherABCStreaming.SearcherABCStreaming):

    tab = ["(Date de sortie)(.*?)$", "(Année de production)(.*?)$","(Nom du film)(.*?)$", "(Réalisé par)(.*?)$","(Avec)(.*?)$","(Genre)(.*?)$","(Durée)(.*?)$","(Nationalité)(.*?)$"]

    def BASE_URL(self):
        return "http://streamay.com"

    '''
    Relative (from root directory of plugin) path to image
    will shown as source image at result listing
    '''
    searchIcon = '/resources/icons/logoStreamy.png'

    @property
    def contentType(self):
        return ContentType.MovieAndTvSerie

    '''
    Main method should be implemented for search process.
    Receives keyword and have to return dictionary of proper tuples:
    '''
    @timed()
    def search(self, keyword, page = 1):
        ## do=search&subaction=search&search_start=2&full_search=0&result_from=0&story=evasion
        filesList = []
        data = {'do':'search',
                'subaction':'search',
                'search_start':str(page),
                'full_search':'0',
                'result_from':'0',
                'story':keyword }

        res = self.GetContentSearchPage(self.BASE_URL(), data)

        for (title, link, imageLink) in res[0]:
            search = self.api.search(title,"movie")
            infoMedia = Media()
            if int(search['feed']['totalResults']) > 0 :
                infoMedia = Utils.GetMediaInfoFromJson(self.api.movie(search['feed']['movie'][0]['code'],"small"), typeMedia="movie")

            if "http://" not in imageLink:
                infoMedia.PictureLink = self.BASE_URL() + imageLink
            else:
                infoMedia.PictureLink = imageLink

            if infoMedia :
                 filesList.append((title,
                    link,
                    infoMedia,
                    self.__class__.__name__,))
            else:
                filesList.append((title,
                    link,
                    None,
                    self.__class__.__name__,))
               
        return filesList

    '''
    Get Info Media from Url
    '''
    def getInfoMediaFromUrl(self, medialink):
        if((re.search(r"/films/", medialink, re.M | re.I) == None) and (re.search(r"/series/", medialink, re.M | re.I) == None)):
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

    def GetContentSearchPage(self, url, data):
        response = self.GetContentFromUrl(url, data)

        tab = []
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
          
            nextPage = soup.find("a", "nextlink")
            if nextPage :
                nextPage = nextPage["href"]
            nodes = soup.findAll("div", "column")
            for node in nodes:
                '''
                @returns title, link, image
                '''
                tab.append((Utils.ClearTitle(node.h3.a.text), node.h3.a["href"].encode('utf-8').strip(), node.div.a.img['src'].encode('utf-8').strip()))
        return (tab, nextPage)

    def GetLinksForPlay(self, url=""):

        if url and url is not None:
            url = urllib.unquote_plus(url)
        else:
            url = urllib.unquote_plus(self.BASE_URL())

        response = Utils.getContentOfUrl(url)
        #if page == 'details':
            #Requête en GET
            #response = Utils.getContentOfUrl(url)
        #else:
        #    #Requête en POST
        #    data = {'dlenewssortby':'date','dledirection':'desc'}
        #    response = Utils.getContentOfUrl(url, data)

        tab = []
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
            #if page == 'details':
            for node in soup.findAll("object"):
                link = node.param["value"]
                tab.append((node.parent.parent.p.img['alt'].encode('utf-8').strip(), link))
            for node in soup.findAll("iframe"):
                if node.has_key("allowfullscreen"):
                   link = node["src"]
                   if 'http://' not in link:
                       link = self.BASE_URL() + link
                   if 'youtube' not in link:
                       tab.append((soup.find('div','describe-box').div.div.img['src'].encode('utf-8').strip(), link))
        return tab

    '''
    liste des épisodes d'une série.
    '''
    def ListEpisodesPageDetailsTvSerie(self, url=""):
        pass

    '''
     Récupération des films depuis la page d'accueil du Site
    '''
    def LatestMovies(self, url):
        tab = []
        #Requête en POST
        data = {'dlenewssortby':'date','dledirection':'desc'}
        response = self.GetContentFromUrl(url, data)
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
            content= soup.find("div", {'id':'dle-content'})
            nodes = content.findAll('div','column')
            self.nextPage = content.find('div','navigation').a['href']
            for node in nodes:
                title = Utils.ClearTitle(node.h3.a.text)
                try:
                    search = self.api.search(title,"movie")
                    infoMedia = Utils.GetMediaInfoFromJson(self.api.movie(search['feed']['movie'][0]['code'],"small"), typeMedia="movie")
                    infoMedia.PictureLink = self.BASE_URL() + node.find('div','image-holder').a.img["src"]
                    infoMedia.Link =node.h3.a["href"].encode('utf-8').strip()
                    infoMedia.Source = self.__class__.__name__
                    tab.append((infoMedia.Title,
                               infoMedia.Link,
                               infoMedia.__dict__,
                               self.__class__.__name__))
                except:
                    #returns title, link, synopsis, img, SearcherName
                    pic = self.BASE_URL() + node.find('div','image-holder').a.img["src"]
                    #returns title, link, synopsis, img, SearcherName
                    tab.append((title,
                               node.h3.a["href"].encode('utf-8').strip(),
                               Media(title, node.h3.a["href"].encode('utf-8').strip(), '', pic, self.__class__.__name__).__dict__,
                               self.__class__.__name__))
                    continue
        return tab

    def AllTvSeries(self):
        return []

    def LatestTvSeriesEpisodes(self, url):
        return []