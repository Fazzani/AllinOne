import sys
import os
from contextlib import contextmanager, closing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))
from xbmcswift2 import Plugin
from default import plugin

FREEBOX_API = 'http://mafreebox.freebox.fr/api/v3'
RESOURCES_PATH = os.path.join(os.path.dirname(sys.modules["__main__"].__file__), 'resources')
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36"
HEADERS={"X-Fbx-App-Auth":"","Host":FREEBOX_API,"Content-Type":"application/json"}
APP_ID = "plugin.video.freeboxtorrent"

def url_get(url, params={}, headers={"Content-Type":"application/json"}, method='AUTO'):
    import urllib2
    import urllib
    plugin.log.info(url)
    plugin.log.info(headers)
    plugin.log.info(params)
    if params and method != 'GET':
        data = repr(params).replace('\'','"').replace(' ','')
        plugin.log.info('data : xxxxxxxxxxxxxxxxx  '+data)
        req = urllib2.Request(url, data)
    else:
        url = "%s?%s" % (url, urllib.urlencode(params))
        req = urllib2.Request(url)

    req.add_header("User-Agent", USER_AGENT)
    for k, v in headers.items():
        req.add_header(k, v)

    try:
        with closing(urllib2.urlopen(req)) as response:
            data = response.read()
            if response.headers.get("Content-Encoding", "") == "gzip":
                import zlib
                return zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(data)
            return data
    except urllib2.HTTPError:
        return None
