import os
import sys
from pathlib import Path

from src import standalone

# Only for development porpoise
if __name__ == '__main__':

    #Create symlinks
    try:
        appPath = os.path.join(sys.executable)
        resourcePath = os.path.join(os.path.dirname(__file__), 'Resources')
        for eachFolder in os.listdir(resourcePath):
            if os.path.isdir(os.path.join(resourcePath, eachFolder)):
                try:
                    os.symlink(src=os.path.join(resourcePath, eachFolder), dst=os.path.join(Path(appPath).parent.absolute(), eachFolder))
                except:
                    pass
    except:
        pass

    standalone()
