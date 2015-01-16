PUBLIC_TRACKERS = [
    "udp://tracker.publicbt.com:80/announce",
    "udp://tracker.openbittorrent.com:80/announce",
    "udp://open.demonii.com:1337/announce",
    "udp://tracker.istole.it:6969",
    "udp://tracker.coppersurfer.tk:80",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}
# Add default trackers to a magnet link, to improve its reachability
def _boost_magnet(magnet):
    from urllib import urlencode
    return "%s&%s" % (magnet, urlencode({"tr": PUBLIC_TRACKERS}, True))


def from_torrent_url(url):
    import base64
    import bencode
    import hashlib
    import urllib
    import urllib2
    from xbmctorrent.utils import url_get
    request = urllib2.Request(url, headers=HEADERS)
    u = urllib2.urlopen(request)
    #meta = u.info()
    #plugin.log.info('----------------------------'  +str(meta))
    #file_size = meta.getheaders("Content-Disposition")[0]
    #file_name=file_size.split('"')[1]
    #plugin.log.info('----------------------------'  +file_name)
    torrent_data = u.read()
    #f = open(file_name, 'rb')
    #plugin.log.info("Downloading: %s Bytes: %s" % (file_name, file_size))
    #plugin.log.info(url)
    #plugin.log.info(torrent_data)
    metadata = bencode.bdecode(torrent_data)
    hashcontents = bencode.bencode(metadata['info'])
    digest = hashlib.sha1(hashcontents).digest()
    b32hash = base64.b32encode(digest)
    params = {
        'dn': metadata['info']['name'],
        'tr': metadata['announce'],
    }
    paramstr = urllib.urlencode(params)
    return 'magnet:?%s&%s' % ('xt=urn:btih:%s' % b32hash, paramstr)


def ensure_magnet(uri):
    if not uri.startswith("magnet:"):
        uri = from_torrent_url(uri)
    return uri


def display_name(magnet_uri):
    import urlparse
    from xbmctorrent.utils import first
    magnet_args = urlparse.parse_qs(magnet_uri.replace("magnet:?", ""))
    return first(magnet_args.get("dn", []))

