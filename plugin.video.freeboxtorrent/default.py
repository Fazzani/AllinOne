from common import *
import xbmc, json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))
from xbmcswift2 import Plugin

plugin = Plugin()

@plugin.route("/")
def listTorrent():
    #authorize()
    listTorrents = requestFreebox(FREEBOX_API + "/downloads/")[CONST_RESULT]
    for torrent in listTorrents:
       file = requestFreebox("%s/downloads/%s/files"%(FREEBOX_API,torrent["id"]))[CONST_RESULT]
       print ( 'Path ===== '+"smb:/"+ xbmc.translatePath(os.path.join("\\\\Freebox", file[0]["path"].encode('utf-8').replace('//','/'))))
       if ('video' or 'stream') in file[0]['mimetype']:
        yield{
            "label": torrent["name"],
            "path":"smb://"+ xbmc.translatePath("Freebox"+ file[0]["path"].encode('utf-8').strip().replace('//','/')),
            "is_playable":True
           }

def authorize():
    params = {"app_id": APP_ID,
              "app_name": "freeboxtorrent",
              "app_version": "0.0.1",
              "device_name": "XBMC"}
    auth = json.loads(url_get(FREEBOX_API + "/login/authorize/", params = params, method='POST'))
    plugin.log.info('auth ____________'+repr(auth))
    if auth['success']:
        plugin.log.info('auth success : '+auth[CONST_RESULT]['app_token'])
        authStorage = plugin.get_storage(name='authStorage', file_format='json', TTL=None)
        authStorage.update({'app_token': auth[CONST_RESULT]['app_token']})

        while 1 == 1:
            res = json.loads(url_get(FREEBOX_API + "/login/authorize/%s" % auth[CONST_RESULT]['track_id']))
            if res['result']['status'] == 'granted':
                plugin.notify('Granted')
                authStorage['challenge'] = res[CONST_RESULT]['challenge']
                authStorage['password'] = getPassword(authStorage['app_token'], authStorage['challenge'])
                authStorage.update({'session': getSession(APP_ID, authStorage['password'])})
                authStorage.sync()
                break
            
            xbmc.sleep(1000)
    else:
        plugin.log.info('auth failed')

def getSession(app_id,password):
    #POST /api/v3/login/session/
    res = json.loads(url_get(FREEBOX_API + "/login/session/",params={"app_id":app_id,"password":password}, method = "POST"))
    print(repr(res))
    if res["result"]:
        return res["result"]
    raise Exception('Getting token session failed')

def getPassword(app_token,challenge):
    from hashlib import sha1
    import hmac
    return hmac.new(app_token.replace('\\','').encode(), challenge.replace('\\',''), sha1).hexdigest()

def requestFreebox(path, params={}, method="GET"):
    authStorage = plugin.get_storage(name='authStorage', file_format='json', TTL=None)
    plugin.log.info('session : ----------- '+str(authStorage.get('session')['session_token']))
    HEADERS["X-Fbx-App-Auth"] = str(authStorage.get('session')['session_token'])
    res = url_get(path, params, HEADERS, method)
    plugin.log.info('______________'+repr(res))
    return json.loads(res)

if __name__ == '__main__':
    try:
        plugin.run()
    except Exception:
        
        raise