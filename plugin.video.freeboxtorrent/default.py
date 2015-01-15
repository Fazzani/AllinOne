import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))
from freebox import monkey_patches
from xbmcswift2 import Plugin

if __name__ == '__main__':
    try:
        plugin = Plugin()
        plugin.run()
    except Exception:
        
        raise
