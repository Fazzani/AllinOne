#-*- coding: utf-8 -*-
import sys
import xbmc
import xbmcvfs
import xbmcaddon
import utils
import time
from datetime import datetime
import re
import urlparse

__addon__ = xbmcaddon.Addon(id='plugin.video.freeboxtorrent')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')


if __name__ == '__main__':
    __delaySettings__ = __addon__.getSetting("delay")
    __PathOfPlayList__ = __addon__.getSetting("path_input")
    if(__PathOfPlayList__== "" ):
      __PathOfPlayList__ = __DefaultPathOfPlayList__
    params = urlparse.parse_qs('&'.join(sys.argv[1:]))
    print(repr(params) + "  ___________________________")
 