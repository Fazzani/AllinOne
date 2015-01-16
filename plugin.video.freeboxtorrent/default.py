from common import *
import xbmc, json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))
from xbmcswift2 import Plugin

plugin = Plugin()

@plugin.route("/")
def listTorrent():
    authorize()
    listTorrents = requestFreebox(FREEBOX_API + "/downloads")
    plugin.log.info(listTorrents)
    for torrent in ListTorrent:
       yield{
            "label": torrent["name"],
            "thumbnail": torrent["image"],
            "path": plugin.url_for(torrent["view"])
           }

def authorize():
    params = {"app_id": APP_ID,
              "app_name": "freeboxtorrent",
              "app_version": "0.0.1",
              "device_name": "XBMC"}
    auth = json.loads(url_get(FREEBOX_API + "/login/authorize/", params = params, method='POST'))
    plugin.log.info('auth ____________'+repr(auth))
    if auth['success']:
        plugin.log.info('auth success : '+auth['result']['app_token'])
        authStorage = plugin.get_storage(name='authStorage', file_format='json', TTL=None)
        authStorage.update({'app_token': auth['result']['app_token']})

        while 1 == 1:
            res = json.loads(url_get(FREEBOX_API + "/login/authorize/%s" % auth['result']['track_id']))
            if res['result']['status'] == 'granted':
                plugin.notify('GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGranted')
                authStorage['challenge'] = res['result']['challenge']
                authStorage['password'] = getPassword(authStorage['app_token'], authStorage['challenge'])
                authStorage.update({'session': getSession(APP_ID, authStorage['password'])})
                plugin.log.info("session = "+authStorage.get('session'))
                authStorage.sync()
                break
            
            xbmc.sleep(1000)
    else:
        plugin.log.info('auth failed')

def getSession(app_id,password):
    #POST /api/v3/login/session/
    res = url_get(FREEBOX_API + "/login/session/",params={"app_id":app_id,"password":password}, method = "POST")
    print(repr(res))
    if res["success"]:
        return res["result"]
    raise Exception('Getting token session failed')

def getPassword(app_token,challenge):
    from hashlib import sha1
    import hmac
    plugin.log.info("app_token : "+app_token)
    plugin.log.info("app_token encoded: "+app_token.replace('\\','').encode())
    plugin.log.info("challenge : "+challenge.replace('\\',''))
    plugin.log.info("challenge modified: "+challenge.replace('\\',''))
    hashed = hmac.new(app_token.replace('\\','').encode(), challenge.replace('\\',''), sha1)
    # The signature
    return hashed.hexdigest()

def requestFreebox(path, params={}, method="GET"):
    authStorage = plugin.get_storage(name='authStorage', file_format='json', TTL=None)
    plugin.log.info('session : ----------- '+str(authStorage.get('session')))
    HEADERS["X-Fbx-App-Auth"] = authStorage.get('session')['session_token']
    return json.dumps(url_get(FREEBOX_API + "/login/session/", params, HEADERS, method))

if __name__ == '__main__':
    try:
        plugin.run()
    except Exception:
        
        raise