import os
import sys
from pathlib import Path

from . import trayStart, standalone

# Only for development porpoise
if __name__ == '__main__':

    #Create symlinks
    try:
        appPath = os.path.join(sys.executable)
        resourcePath = os.path.join(os.path.dirname(__file__), 'Resources')
        for eachFolder in os.listdir(resourcePath):
            os.symlink(src=os.path.join(resourcePath, eachFolder), dst=os.path.join(Path(appPath).parent.absolute(), eachFolder))
    except:
        pass

    standalone()
