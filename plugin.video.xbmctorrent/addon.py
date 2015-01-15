import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))
from freebox import monkey_patches, plugin
from xbmcswift2 import Plugin

plugin = Plugin()

if __name__ == '__main__':
    try:
        plugin.run()
    except Exception, e:
        import xbmc
        import traceback
        map(xbmc.log, traceback.format_exc().split("\n"))
        raise
