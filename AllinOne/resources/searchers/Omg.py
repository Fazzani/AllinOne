#-*- coding: utf-8 -*-
'''
    Torrenter plugin for XBMC
    Copyright (C) 2012 Vadim Skorba
    vadim.skorba@gmail.com

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
from Utils import timed, tryGetValue


class Omg(SearcherABC.SearcherABC):

    tab =["(Date de sortie)(.*?)$", "(Année de production)(.*?)$","(Nom du film)(.*?)$", "(Réalisé par)(.*?)$","(Avec)(.*?)$","(Genre)(.*?)$","(Durée)(.*?)$","(Nationalité)(.*?)$"]

    BASE_URL = "http://www.omgtorrent.com"

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
    searchIcon = '/resources/icons/logoOmg.png'

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
        #http://www.omgtorrent.com/recherche/?order=seeders&orderby=desc&query=Red
        url = self.BASE_URL + "/recherche/?order=seeders&orderby=desc&query=%s&page=%s" % (urllib.quote_plus(keyword))
        #print url
        response = self.makeRequest(url)
        if None != response and 0 < len(response):
            soup = BeautifulSoup(response)
            nodes = soup.findAll("tr", "table_corps")
            image = sys.modules[ "__main__"].__root__ + self.searchIcon

            #print response
            for node in nodes:
                seeds= node.findAll("td","clients")[0].text
                leechers= node.findAll("td","sources")[0].text
                titleTorrent = node.findAll("a","torrent")[0].text
                medialink = node("td")[1].a["href"]
                size=node("td")[2].strong.text
                #print "_______________ " + titleTorrent

                torrentTitle = "%s [S\L: (%s\%s) %s]" % (titleTorrent, seeds, leechers, size)
                match = re.match(r'(.+?)_([0-9]+?).html', medialink)
                if match :
                    link = self.BASE_URL + "/clic_dl.php?id=%s" % match.group(2)
                else:
                    return []

                filesList.append((
                    int(int(self.sourceWeight) * int(seeds)),
                    int(seeds),
                    self.__class__.__name__ + '::' + link,
                    self.getInfoMediaFromUrl,
                    self.BASE_URL + medialink,
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

