Plugin requires python binding

--- INSTALLATION ---

1. Windows
1.1 Download from 'http://code.google.com/p/libtorrent/downloads/list'
    last version of installer for windows, at the moment
    it is 'python-libtorrent-0.16.0.win32-py2.6.msi'
1.2 Run installer and point as an installation directory - directory of 
    python for xbmc. Usually it is 'C:\Program Files (x86)\XBMC\system\python'
1.3 Install addon and enjoy

2. Linux
2.1 Run at console 'sudo apt-get install python-libtorrent'
2.2 Install addon and enjoy

or you could compile it:

sudo apt-get install libboost-dev libboost-python-dev libboost-system-dev g++ libssl openssl autotool automake subversion
svn co https://libtorrent.svn.sourceforge.net/svnroot/libtorrent/trunk/ lt/
cd lt/
./autotool.sh
./configure
make
sudo make install
sudo ldconfig
