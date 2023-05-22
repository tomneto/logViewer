import os
import subprocess
import sys
import tempfile
from sys import platform

import PyInstaller
import shutil
import PyInstaller.__main__

def run(dest):
    temp = tempfile.mkdtemp(suffix='logViewer')
    ExecutableName = 'LogViewer'

    PyInstaller.__main__.run([
        f'{os.path.join(os.path.dirname(__file__), "run.py")}',
        f'--name={ExecutableName}',
        '--noconfirm',
        #'--uac-admin',
        #f'--icon={os.path.join(os.path.dirname(__file__), "Resources", "ico.ico")}',
        #f'--add-data={os.path.join(os.path.dirname(__file__), "Settings")};Settings/',
        ##f'--add-data={os.path.join(os.path.dirname(__file__), "Resources")};Resources/',
       # f'--add-data={os.path.join(os.path.dirname(__file__), "Bin")};Bin/',
        #'--hidden-import=win32timezone',
        #'--hidden-import=patool',
        #'--hidden-import=patool.programs',
        #'--hidden-import=patool.programs.p7zip'
        #'--hidden-import=pyunpack',
        '--onefile',
        '--windowed',
        f'--workpath={temp}',
        f'--distpath={dest}'
    ])

    FilePath = [temp, f'{ExecutableName}.spec']

    for item in FilePath:
        if os.path.isfile(item):
            os.remove(item)
            print(f"{item} been deleted")
        if os.path.isdir(item):
            shutil.rmtree(item)
            print(f"{item} been deleted")
        else:
            print(f"{item} does not exist")

    #if sys.platform == 'darwin':


run('Dist')