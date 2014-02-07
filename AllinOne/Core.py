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
import Downloader
import Localization
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import urllib
import urllib2
import re
import tempfile
import time
import cookielib
import json
import xml.dom.minidom
import os.path
from Utils import *
import Utils
import urlresolver
from allocine.Allocine import Allocine
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/resources/searchersStreaming/'))
from Media import Media
class Core:
   
    Debug = True
    __plugin__ = sys.modules["__main__"].__plugin__
    __settings__ = sys.modules["__main__"].__settings__
    plugin_handle = int(sys.argv[1])
    _pluginName = (sys.argv[0])
    ROOT = sys.modules["__main__"].__root__#.encode(sys.getfilesystemencoding())
    userStorageDirectory = __settings__.getSetting("storage")
    USERAGENT = "Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.0"
    URL = 'http://torrenter.host.org'
    torrentFilesDirectory = 'torrents'
    api = Allocine()
    __cache__ = sys.modules["__main__"].__cache__

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
    skinOptimizations = ({#Confluence
            'list': 50,
            'info': 50,
            'wide': 51,
            'icons': 500,
        },
        {#Transperency!
            'list': 50,
            'info': 51,
            'wide': 52,
            'icons': 53,
        })

    def __init__(self):
        
        self.api.configure('100043982026','29d185d98c984a359e6e6f26a0474269')
        if 0 == len(self.userStorageDirectory):
            self.userStorageDirectory = tempfile.gettempdir() + os.path.sep + 'Torrenter'
        else:
            self.userStorageDirectory = self.userStorageDirectory + 'Torrenter'
        try:
            import StorageServer
        except:
            import storageserverdummy as StorageServer
        if(self.Debug):
            self.__cache__ = StorageServer.StorageServer(self._pluginName, 0) # (Your plugin name, Cache time in hours)
        else:
            self.__cache__ = StorageServer.StorageServer(self._pluginName, 0.5) # (Your plugin name, Cache time in hours)

    def drawItem(self, title, action, link='', image='', isFolder=True, contextMenu=None, infoMedia=None, searcherName='', page=1, method="search"):
        listitem = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
        url = '%s?action=%s&url=%s&searcherName=%s&page=%s&method=%s' % (sys.argv[0], action, urllib.quote_plus(link), searcherName, str(page), method)
        if contextMenu:
            listitem.addContextMenuItems(contextMenu, replaceItems=True)
        if isFolder:
            listitem.setProperty("Folder", "true")
        else:
            listitem.setInfo(type = 'Video', infoLabels = {"Title":title })

        if infoMedia is not None:
            listitem.setInfo(type = 'Video', infoLabels = {"Title": infoMedia.Title ,"Year": infoMedia.Year, "Genre" : infoMedia.Genre , "Country" : infoMedia.Country,"Plot": infoMedia.Plot,"Director": infoMedia.Director,"Duration":infoMedia.Duration,"Cast": infoMedia.Cast})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=isFolder)

    '''
    '''
    def sectionMenu(self):
        self.drawItem(Localization.localize('< Search >'), 'search', image=self.ROOT + '/icons/search.png')
        self.drawItem('Chercher un streaming', 'searchStreaming', image=self.ROOT + '/icons/search.png')
        self.drawItem('Les derniers films', 'openSectionStreaming', image=self.ROOT + '/resources/icons/logoStreamy.png', method="LatestMovies")
        self.drawItem('Les dernières séries', 'openSectionStreaming', image=self.ROOT + '/resources/icons/RFS.png', method="AllTvSeries")
        self.drawItem('Les derniers épisodes', 'openSectionStreaming', image=self.ROOT + '/resources/icons/RFS.png', method="LatestTvSeriesEpisodes")
        self.drawItem('urlresolver Settings', 'display_settings', image=self.ROOT + '/icons/Settings.png')

        '''self.drawItem(Localization.localize('< Popular >'), 'getPopular', image=self.ROOT + '/icons/video.png')
        self.drawItem(Localization.localize('< Ratings >'), 'getRatings', image=self.ROOT + '/icons/video.png')
        self.drawItem(Localization.localize('< Recent Materials >'), 'recentMaterilas', image=self.ROOT + '/icons/video.png')
        if self.__settings__.getSetting("auth"):
            self.drawItem(Localization.localize('< Bookmarks >'), 'getBookmarks', image=self.ROOT + '/icons/bookmarks.png')
            self.drawItem(Localization.localize('< History >'), 'getHistory', image=self.ROOT + '/icons/history.png')
            self.drawItem(Localization.localize('< Logout >'), 'logoutUser', image=self.ROOT + '/icons/logout.png')
        else:
            self.drawItem(Localization.localize('< Login >'), 'loginUser', image=self.ROOT + '/icons/login.png')
            self.drawItem(Localization.localize('< Register >'), 'registerUser', image=self.ROOT + '/icons/register.png')'''
        if 'true' == self.__settings__.getSetting("keep_files"):
            self.drawItem(Localization.localize('< Clear Storage >'), 'clearStorage', isFolder = True)
        self.lockView('list')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def play_video_stream(self, params={}):
        url = params.get("url")
        searcherName = params.get("searcherName")
        searcherObject = self.getSearcherStreaming(searcherName)
        if searcherObject is None :
            return
        dict = searcherObject.GetLinksForPlay(url)
        self.playVideo(dict)

    '''
    Play Vidéo from a dict (title, link of stream)
    '''
    def playVideo(self, dict):
        for title, linkStrm  in dict:
            try:
                if re.match('http://(.*)vk\.(com|me)/(.*)', linkStrm):
                    stream_url = Utils.VK_ResolveUrl(linkStrm)
                else:
                    stream_url = urlresolver.resolve(linkStrm)
                
                if stream_url:
                    #print(stream_url)
                    #print("Source : %s" % Utils.GetDomain(linkStrm))
                    listitem = xbmcgui.ListItem(title)
                    listitem.setInfo(type = 'Video', infoLabels = {"Title": title})
                    search = self.api.search(title, "tvseries")
                    if int(search['feed']['totalResults']) > 0 :
                        infoMedia = Utils.GetMediaInfoFromJson(self.api.tvseries(search['feed']['tvseries'][0]['code'],"small"))
                        listitem.setInfo(type = 'Video', infoLabels = {"Title": infoMedia.Title, "Year": infoMedia.Year, "Genre" : infoMedia.Genre , "Country" : infoMedia.Country,"Plot": infoMedia.Plot,"Director": infoMedia.Director,"Duration":infoMedia.Duration,"Cast": infoMedia.Cast})

                    xbmc.Player().play(stream_url, listitem)
                    break
                else:
                    continue

            except Exception,e:
                print(e)
                continue
    '''
    Crée un objet Searcher's Streaming
    '''
    def getSearcherStreaming(self, searcherName):
        if self.ROOT + os.sep + 'resources' + os.sep + '\searchersStreaming' not in sys.path:
            sys.path.insert(0, self.ROOT + os.sep + 'resources' + os.sep + '\searchersStreaming')
        try:
            print searcherName
            return getattr(__import__(searcherName), searcherName)()
        except Exception, e:
            print 'Unable to use searcher: ' + searcher + ' at ' + self.__plugin__ + ' searchWithSearcherStreaming(). Exception: ' + str(e)
            return None
        
    def searchStreaming(self, params={}):
        defaultKeyword = params.get('url')
        if not defaultKeyword:
            defaultKeyword = ''
        keyboard = xbmc.Keyboard(defaultKeyword, Localization.localize('Search Phrase') + ':')
        keyboard.doModal()
        query = keyboard.getText()
        if not query:
            return
        elif keyboard.isConfirmed():
            params["url"] = urllib.quote_plus(query)
            params["method"] = urllib.quote_plus("search")
            self.openSectionStreaming(params)

    def openSectionStreaming(self, params={}):
        get = params.get
        query = get("url")
        if query:
            query = urllib.unquote_plus(query)
        method = get("method")
        filesList = []
        if None == get('isApi'):
            progressBar = xbmcgui.DialogProgress()
            progressBar.create(Localization.localize('Please Wait'), Localization.localize('Materials are loading now.'))
            iterator = 0
        searchersList = []
        dirList = os.listdir(self.ROOT + os.sep + 'resources' + os.sep + 'searchersStreaming')
        for searcherFile in dirList:
            if re.match('^(\w+)\.py$', searcherFile):
                searchersList.append(searcherFile)
        for searcherFile in searchersList:
            searcher = re.search('^(\w+)\.py$', searcherFile).group(1)
            #print searcher
            if searcher:
                if None == get('isApi'):
                    progressBar.update(int(iterator), "Seaching in [COLOR F6D8CE00][B]%s[/B][/COLOR] site " % searcher)
                    iterator += 100 / len(searchersList)
                filesList += self.searchWithSearcherStreaming(query, searcher, method)
                
            if None == get('isApi') and progressBar.iscanceled():
                progressBar.update(0)
                progressBar.close()
                return
        if None == get('isApi'):
            progressBar.update(0)
            progressBar.close()
        self.showFilesStreamingList(sorted(filesList, key= lambda x: x[0]), method)

    def showFilesStreamingList(self, filesList, method):
        for (title, link, infoMedia, searcherName) in filesList:
            media = Utils.obj_dic(infoMedia)
            #print link
            if infoMedia :
                if(method == "AllTvSeries"):
                    self.drawItem(" [COLOR F6D8CE00][B]%s[/B][/COLOR] (%s) " % (title, searcherName), 'open_TvSeriePage', 
                                  link, media.PictureLink, infoMedia = media, searcherName= searcherName, isFolder = True, method = method)
                else:
                    self.drawItem(" [COLOR F6D8CE00][B]%s[/B][/COLOR] (%s) " % (title, searcherName), 'play_video_stream', 
                                  link, media.PictureLink, infoMedia = media, searcherName = searcherName, method = method)
            else:
                if(method == "AllTvSeries"):
                    self.drawItem(title, 'open_TvSeriePage', link, isFolder=True, searcherName = searcherName, method = method)
                else:
                    self.drawItem(title, 'play_video_stream', link, searcherName = searcherName, method = method)
        #self.lockView('wide')
        #if res[1] != None:
        #    self.drawItem("Next Page >>", 'openSectionStreaming', res[1])
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
    '''
    Lister les épisodes d'une série
    '''
    def open_TvSeriePage(self, params={}):

        get = params.get
        url = get("url")
        if url:
            url = urllib.unquote_plus(url)
        method = get("method")
        searcher = get("searcherName")
        filesList = []
        if self.ROOT + os.sep + 'resources' + os.sep + '\searchersStreaming' not in sys.path:
            sys.path.insert(0, self.ROOT + os.sep + 'resources' + os.sep + '\searchersStreaming')
        try:
            searcherObject = getattr(__import__(searcher), searcher)()
            #print url
            filesList = searcherObject.ListEpisodesPageDetailsTvSerie(url)
            self.ShowListVideosLinks(sorted(filesList, key= lambda x: x[0]))

        except Exception, e:
            print 'Unable to use searcher: ' + searcher + ' at ' + self.__plugin__ + ' open_TvSeriePage(). Exception: ' + str(e)
            self.ShowListVideosLinks(sorted(filesList, key= lambda x: x[0]))
        pass

    '''
    Récupérer les liens de streaming 
    '''
    def ShowListVideosLinks(self, filesList):
        for (title, link, infoMedia, searcherName) in filesList:
            media = Utils.obj_dic(infoMedia)
            if infoMedia :
                self.drawItem(" [COLOR F6D8CE00][B]%s[/B][/COLOR] (%s) " % (title, searcherName), 'open_link_video_Item', 
                                  link, media.PictureLink, infoMedia = media, searcherName = searcherName)
            else:
                self.drawItem(title, 'open_link_video_Item', link, searcherName = searcherName)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
        
    def open_link_video_Item(self, params={}):
        get = params.get
        url = get("url")
        if url:
            url = urllib.unquote_plus(url)
        searcher = get("searcherName")
        filesList = []
        if self.ROOT + os.sep + 'resources' + os.sep + '\searchersStreaming' not in sys.path:
            sys.path.insert(0, self.ROOT + os.sep + 'resources' + os.sep + '\searchersStreaming')
        try:
            searcherObject = getattr(__import__(searcher), searcher)()
            filesList = searcherObject.GetLinksForPlay(url)
            index = xbmcgui.Dialog().select('Choose a source', map(lambda x, y: '[COLOR F6D8CE00][B]Link %s [/B][/COLOR](%s)' % (x, Utils.GetDomain(y[1])), range(len(filesList)),filesList))
            tabLink=[]
            tabLink.append(filesList[index])
            self.playVideo(tabLink)

        except Exception, e:
            print 'Unable to use searcher: ' + searcher + ' at ' + self.__plugin__ + ' open_link_video_Item(). Exception: ' + str(e)
            #self.play_video_stream(sorted(filesList, key= lambda x: x[0]),'')
        
    '''
    Open Section for Torrent
    '''
    def openSection(self, params={}):
        get = params.get
        url = urllib.unquote_plus(get("url"))
        filesList = []
        if None == get('isApi'):
            progressBar = xbmcgui.DialogProgress()
            progressBar.create(Localization.localize('Please Wait'), Localization.localize('Materials are loading now.'))
            iterator = 0
        searchersList = []
        dirList = os.listdir(self.ROOT + os.sep + 'resources' + os.sep + 'searchers')
        for searcherFile in dirList:
            if re.match('^(\w+)\.py$', searcherFile):
                searchersList.append(searcherFile)
        for searcherFile in searchersList:
            searcher = re.search('^(\w+)\.py$', searcherFile).group(1)
            if searcher:
                if None == get('isApi'):
                    progressBar.update(int(iterator), searcher)
                    iterator += 100 / len(searchersList)
                print('Searching .... with %s' % searcher)
                filesList += self.searchWithSearcher(url, searcher)
            if None == get('isApi') and progressBar.iscanceled():
                progressBar.update(0)
                progressBar.close()
                return
        if None == get('isApi'):
            progressBar.update(0)
            progressBar.close()
        filesList = sorted(filesList, key=lambda x: x[0], reverse=True)
        self.showFilesList(filesList)

    def display_settings(self, params={}):
        urlresolver.display_settings()

    '''
    Searching in torrents
    '''
    def searchWithSearcher(self, keyword, searcher):
        filesList = []
        if self.ROOT + os.sep + 'resources' + os.sep + 'searchers' not in sys.path:
            sys.path.insert(0, self.ROOT + os.sep + 'resources' + os.sep + 'searchers')
        try:
            searcherObject = getattr(__import__(searcher), searcher)()
            if searcherObject.isMagnetLinkSource and 'false' == self.__settings__.getSetting("use_magnet_links"):
                return filesList
            filesList = searcherObject.search(keyword)
        except Exception, e:
            print 'Unable to use searcher: ' + searcher + ' at ' + self.__plugin__ + ' searchWithSearcher(). Exception: ' + str(e)
        return filesList

    '''
    Searching in streaming sites
    '''
    def searchWithSearcherStreaming(self, keyword, searcher, method="search"):
        filesList = []
        if self.ROOT + os.sep + 'resources' + os.sep + '\searchersStreaming' not in sys.path:
            sys.path.insert(0, self.ROOT + os.sep + 'resources' + os.sep + '\searchersStreaming')
        try:
            searcherObject = getattr(__import__(searcher), searcher)()
            if(method == "search"):
                filesList = searcherObject.search(keyword)
            if(method == "LatestMovies"):
                filesList = self.__cache__.cacheFunction(searcherObject.LatestMovies, keyword)
            if(method == "AllTvSeries"):
                filesList = self.__cache__.cacheFunction(searcherObject.AllTvSeries)
                #filesList = searcherObject.AllTvSeries()
            if(method == "LatestTvSeriesEpisodes"):
                filesList = self.__cache__.cacheFunction(searcherObject.LatestTvSeriesEpisodes, keyword)

        except Exception, e:
            print 'Unable to use searcher: ' + searcher + ' at ' + self.__plugin__ + ' searchWithSearcherStreaming(). Exception: ' + str(e)
        return filesList
    
    @timed()
    def showFilesList(self, filesList):
        for (order, seeds, link, func, medialink) in filesList:
            '''contextMenu = [(
                Localization.localize('Add To Bookmarks'),
                'XBMC.RunPlugin(%s)' % ('%s?action=%s&url=%s&name=%s&seeds=%s&image=%s') % (sys.argv[0], 'addBookmark', urllib.quote_plus(link), urllib.quote_plus(title), seeds, urllib.quote_plus(image))
            )]'''
            mediaInfo = func(medialink)
            #print mediaInfo.Title
            if mediaInfo is not None:
                self.drawItem(mediaInfo.Title, 'openTorrent', link, mediaInfo.PictureLink, infoMedia = mediaInfo)
        #self.lockView('wide')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def fetchData(self, url, referer=None):
        request = urllib2.Request(url)
        if referer != None:
            request.add_header('Referer', referer)
        request.add_header('User-Agent', self.USERAGENT)
        if self.__settings__.getSetting("auth"):
            authString = '; ' + self.__settings__.getSetting("auth")
        else:
            authString = ''
        request.add_header('Cookie', authString)
        try:
            connection = urllib2.urlopen(request)
            result = connection.read()
            connection.close()
            return (result)
        except (urllib2.HTTPError, urllib2.URLError) as e:
            print self.__plugin__ + " fetchData(" + url + ") exception: " + str(e)
            return

    def lockView(self, viewId):
        if 'true' == self.__settings__.getSetting("lock_view"):
            try:
                xbmc.executebuiltin("Container.SetViewMode(%s)" % str(self.skinOptimizations[int(self.__settings__.getSetting("skin_optimization"))][viewId]))
            except:
                return

    def getParameters(self, parameterString):
        commands = {}
        splitCommands = parameterString[parameterString.find('?') + 1:].split('&')
        for command in splitCommands:
            if (len(command) > 0):
                splitCommand = command.split('=')
                if (len(splitCommand) > 1):
                    name = splitCommand[0]
                    value = splitCommand[1]
                    commands[name] = value
        return commands

    def unescape(self, string):
        for (symbol, code) in self.htmlCodes:
            string = re.sub(code, symbol, string)
        return string

    def stripHtml(self, string):
        for (html, replacement) in self.stripPairs:
            string = re.sub(html, replacement, string)
        return string

    def executeAction(self, params={}):
        get = params.get
        if hasattr(self, get("action")):
            getattr(self, get("action"))(params)
        else:
            self.sectionMenu()

    def clearStorage(self, params={}):
        #if os.path.exists(self.userStorageDirectory):
        if xbmcvfs.exists(self.userStorageDirectory):
            import shutil
            shutil.rmtree(self.userStorageDirectory, ignore_errors=True)
        xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Storage'), Localization.localize('Storage was cleared')))

    def calculateIterator(self, current, full):
        if (100 * 1024 * 1024) > full:#<100Mb
            return current * (100 / 25 * 100) / full# 25% of file size = 100% of progress
        elif (500 * 1024 * 1024) > full:#<500Mb
            return current * (100 / 7 * 100) / full# 7% of file size = 100% of progress
        elif (2000 * 1024 * 1024) > full:#<2000Mb
            return current * (100 / 3 * 100) / full# 3% of file size = 100% of progress
        elif (4000 * 1024 * 1024) > full:#<4000Mb
            return current * (100 / 1 * 100) / full# 1% of file size = 100% of progress
        else:#>4000Mb
            return current * 100 / (50 * 1024 * 1024)# 50Mb file size = 100% of progress

    def playTorrent(self, params={}):
        torrentUrl = self.__settings__.getSetting("lastTorrent")
        if 0 != len(torrentUrl):
            get = params.get
            contentId = int(get("url"))
            torrent = Downloader.Torrent(self.userStorageDirectory, torrentUrl, self.torrentFilesDirectory)
            if 'false' == self.__settings__.getSetting("keep_seeding"):
                torrent.startSession(contentId, seeding=False)
            else:
                torrent.startSession(contentId)
            if 0 < int(self.__settings__.getSetting("upload_limit")):
                torrent.setUploadLimit(int(self.__settings__.getSetting("upload_limit")) * 1000000 / 8) #MBits/second
            if 0 < int(self.__settings__.getSetting("download_limit")):
                torrent.setDownloadLimit(int(self.__settings__.getSetting("download_limit")) * 1000000 / 8) #MBits/second
            iterator = 0
            progressBar = xbmcgui.DialogProgress()
            progressBar.create(Localization.localize('Please Wait'), Localization.localize('Seeds searching.'))
            fullSize = torrent.getFileSize(contentId)
            downloadedSize = 0
            while iterator < 100 and downloadedSize < (45 * 1024 * 1024):#45Mb
                time.sleep(1)
                downloadedSize = torrent.torrentHandle.file_progress()[contentId]
                iterator = self.calculateIterator(downloadedSize, fullSize)
                dialogText = Localization.localize('Preloaded: ') + str(downloadedSize / 1024 / 1024) + ' MB / ' + str(fullSize / 1024 / 1024) + ' MB'
                peersText = ' [%s: %s; %s: %s]' % (Localization.localize('Seeds'), str(torrent.getSeeds()), Localization.localize('Peers'), str(torrent.getPeers()))
                speedsText = '%s: %s Mbit/s; %s: %s Mbit/s' % (Localization.localize('Downloading'), str(torrent.getDownloadRate() * 8 / 1000000), Localization.localize('Uploading'), str(torrent.getUploadRate() * 8 / 1000000))
                progressBar.update(iterator, Localization.localize('Seeds searching.') + peersText, dialogText, speedsText)
                if progressBar.iscanceled():
                    progressBar.update(0)
                    progressBar.close()
                    torrent.threadComplete = True
                    return
            progressBar.update(0)
            progressBar.close()

            from Proxier import Proxier
            import thread
            proxier = Proxier()
            #thread.start_new_thread(proxier.server,
            #(torrent.getFilePath(contentId), ))
            #xbmc.Player().play('http://127.0.0.1:51515/play.avi')
            #return

            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()
            listitem = xbmcgui.ListItem(torrent.getContentList()[contentId].path)
            playlist.add('file:///' + torrent.getFilePath(contentId), listitem)
            #playlist.add('http://127.0.0.1:51515/%s.avi' %
            #torrent.md5(torrent.getFilePath(contentId)), listitem)
            xbmc.Player().play(playlist)
            #self.addHistory(torrent.getContentList()[contentId].path)
            #bufferingBar = xbmcgui.DialogProgress()
            while 1 == xbmc.Player().isPlayingVideo():
                torrent.fetchParts()
                torrent.checkThread()
                time.sleep(1)
                '''if proxier.seekBytes > 0:
                    torrent.fetchSeekBytes(proxier.seekBytes)
                    proxier.seekBytes = 0
                if proxier.buffering > 0:
                    bufferingBar.create(Localization.localize('Please Wait'), Localization.localize('Buffering...'))
                    bufferingBar.update(proxier.buffering / 60 * 100)
                    if bufferingBar.iscanceled():
                        bufferingBar.update(0)
                        bufferingBar.close()
                        torrent.threadComplete = True
                        return
                else:
                    try:
                        bufferingBar.update(0)
                        bufferingBar.close()
                    except:
                        pass'''

            if 'false' == self.__settings__.getSetting("keep_files"):
                torrent.threadComplete = True
                self.clearStorage()
            else:
                dialog = xbmcgui.Dialog()
                if dialog.yesno(Localization.localize('Torrent Downloading'),
                    Localization.localize('Do you want to STOP torrent downloading and seeding?'),
                    Localization.localize('Preloaded: ') + str(downloadedSize / 1024 / 1024) + ' MB / ' + str(fullSize / 1024 / 1024) + ' MB'):
                    xbmc.executebuiltin("Notification(%s, %s)" % (Localization.localize('Information'), Localization.localize('Torrent downloading is stopped.')))
                    torrent.threadComplete = True
            #self.addRate(torrent.getContentList()[contentId].path)
        else:
            print self.__plugin__ + " Unexpected access to method playTorrent() without torrent content"

    def openTorrent(self, params={}):
        get = params.get
        url = urllib.unquote_plus(get("url"))
        self.__settings__.setSetting("lastTorrentUrl", url)
        classMatch = re.search('(\w+)::(.+)', url)
        if classMatch:
            searcher = classMatch.group(1)
            #print "openTorrent............................" + classMatch.group(2)
            if self.ROOT + os.sep + 'resources' + os.sep + 'searchers' not in sys.path:
                sys.path.insert(0, self.ROOT + os.sep + 'resources' + os.sep + 'searchers')
            try:
                searcherObject = getattr(__import__(searcher), searcher)()
            except Exception, e:
                print 'Unable to use searcher: ' + searcher + ' at ' + self.__plugin__ + ' openTorrent(). Exception: ' + str(e)
                return
            url = searcherObject.getTorrentFile(classMatch.group(2))
        torrent = Downloader.Torrent(self.userStorageDirectory, torrentFilesDirectory = self.torrentFilesDirectory)
        self.__settings__.setSetting("lastTorrent", torrent.saveTorrent(url))
        contentId = 0
        #listitem = xbmcgui.ListItem('<' + Localization.localize('Add To
        #Bookmarks') + ' >')
        #itemUrl = '%s?action=%s&url=%s&name=%s&seeds=%s&image=%s' %
        #(sys.argv[0], 'addBookmark', urllib.quote_plus(url),
        #urllib.quote_plus(torrent.getContentList()[0].path), 0, '')
        #listitem.setInfo(type = 'Video', infoLabels = {"Title":'<' +
        #Localization.localize('Add To Bookmarks') + ' >'})
        #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemUrl,
        #listitem=listitem)
        contentList = []
        for contentId, contentFile in enumerate(torrent.getContentList()):
            fileTitle = "%s [%s MB]" % (contentFile.path, contentFile.size / 1024 / 1024)#In MB
            contentList.append((self.unescape(fileTitle), str(contentId)))
        contentList = sorted(contentList, key=lambda x: x[0])
        for title, identifier in contentList:
            self.drawItem(title, 'playTorrent', identifier, isFolder=False)
        self.lockView('info')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def search(self, params={}):
        defaultKeyword = params.get('url')
        if not defaultKeyword:
            defaultKeyword = ''
        keyboard = xbmc.Keyboard(defaultKeyword, Localization.localize('Search Phrase') + ':')
        keyboard.doModal()
        query = keyboard.getText()
        if not query:
            return
        elif keyboard.isConfirmed():
            params["url"] = urllib.quote_plus(query)
            self.openSection(params)

   