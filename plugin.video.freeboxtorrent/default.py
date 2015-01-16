from common import *
import xbmc
import json
import sys
import os
from magnet import ensure_magnet

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))
from xbmcswift2 import Plugin

plugin = Plugin()

@plugin.route("/")
def listTorrent():
    import base64
    listTorrents = requestFreebox(FREEBOX_API + "/downloads/")[CONST_RESULT]
    for torrent in listTorrents:
       file = requestFreebox("%s/downloads/%s/files" % (FREEBOX_API,torrent["id"]))[CONST_RESULT]
       if ('video' or 'stream') in file[0]['mimetype']:
           path = xbmc.translatePath("smb://Freebox" + (base64.b64decode(torrent['download_dir'])+file[0]['name'].encode('utf-8')))
           plugin.log.info(path)
           yield{
                "label": torrent["name"],
                "path":path,
                "is_playable":True
            }
    yield{
          "label": "Add Torrent",
          "path":plugin.url_for("addByUrl",url="http://www.omgtorrent.com/clic_dl.php?id=22147"),
          "is_playable":False
        }

#POST /api/v3/downloads/add
@plugin.route("/downloads/addUrl/<url>")
def addByUrl(url):
    #plugin.log.info('Magnet uri : '+ensure_magnet(url))
    res = requestFreeboxWithChaine("%s/downloads/add" % FREEBOX_API, dict(download_url=url) ,{"Content-Type":"application/x-www-form-urlencoded","Accept": "text/plain"})
    plugin.log.info('AddByUrl : ' + repr(res))
    return {
          "label": "Torrent added",
          "path":"",
          "is_playable":False
        }

#POST /api/v3/downloads/add (multipart/form-data)
@plugin.route("/downloads/addfile/<file>")
def addByFile(file):
    res = requestFreeboxWithChaine("%s/downloads/add" % FREEBOX_AP,"download_url:"+ ensure_magnet(url),{"Content-Type":"multipart/form-data;charset=UTF-8"})
    plugin.log.info('AddByUrl : ' + repr(res))
    return res

def authorize():
    
    params = {"app_id": APP_ID,
              "app_name": plugin.addon.getAddonInfo('name'),
              "app_version": plugin.addon.getAddonInfo('version'),
              "device_name": DEVICE_NAME }
    auth = json.loads(url_get(FREEBOX_API + "/login/authorize/", params = params, method='POST'))
    plugin.log.info('auth ____________' + repr(auth))
    if auth['success']:
        plugin.log.info('auth success : ' + auth[CONST_RESULT]['app_token'])
        authStorage = plugin.get_storage(name='authStorage', file_format='json', TTL=None)
        authStorage.update({'app_token': auth[CONST_RESULT]['app_token']})
        authStorage.update({'track_id': auth[CONST_RESULT]['track_id']})
        authStorage.sync()

        while 1 == 1:
           if not openSession():
                break
        xbmc.sleep(1000)
    else:
        plugin.log.info('auth failed')

def openSession():
    authStorage = plugin.get_storage(name='authStorage', file_format='json', TTL=None)
    print('________________________' + authStorage['track_id'])
    res = json.loads(url_get(FREEBOX_API + "/login/authorize/%s" % 46))
    print(res)
    if res['result']['status'] == 'granted' or res['result']['status']=='timeout':
       authStorage['challenge'] = res[CONST_RESULT]['challenge']
       authStorage['password'] = getPassword(authStorage['app_token'], authStorage['challenge'])
       authStorage.update({'session': getSession(APP_ID, authStorage['password'])})
       authStorage.sync()
       return True
    return False

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

def requestFreeboxWithChaine(path, params,headers={}):
    authStorage = plugin.get_storage(name='authStorage', file_format='json', TTL=None)
    plugin.log.info('session : ----------- ' + str(authStorage.get('session')['session_token']))
    HEADERS["X-Fbx-App-Auth"] = str(authStorage.get('session')['session_token'])
    for key,value in headers.items(): 
        HEADERS[key]=value
    res = url_get_param_string(path, params, HEADERS)
    plugin.log.info(repr(res))
    if res is None:
       if openSession():
            requestFreeboxWithChaine(path,params,headers)
       else:
            plugin.notify('Failed to open session')
    return json.loads(res)

def requestFreebox(path, params={}, method="GET", headers={}):
    authStorage = plugin.get_storage(name='authStorage', file_format='json', TTL=None)
    plugin.log.info('session : ----------- ' + str(authStorage.get('session')['session_token']))
    HEADERS["X-Fbx-App-Auth"] = str(authStorage.get('session')['session_token'])
    for key,value in headers.items(): 
        HEADERS[key]=value
    res = url_get(path, params, HEADERS, method)
    plugin.log.info(repr(res))
    if res is None:
       if openSession():
            requestFreebox(path,params,method,headers)
       else:
            plugin.notify('Failed to open session')
    return json.loads(res)

if __name__ == '__main__':
    try:
        plugin.run()
    except Exception:
        
        raise