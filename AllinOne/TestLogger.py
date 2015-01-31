import sys
if (__name__ == "__main__"):
    import urllib2, json
    url = 'http://xbmcplugindata.azurewebsites.net/logger/send'
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent, 'Content-Type'  : 'application/json'}
   
    request = urllib2.Request(url, data = json.dumps({'level':'Error','source':'source','message':'message python '}), headers= headers)

    response = urllib2.urlopen(request).read()
    print repr(response)
    