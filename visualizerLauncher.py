import webbrowser
import subprocess
import os
import sys

def launchVis(data=None):
    subprocess.Popen([os.path.dirname(sys.executable)+"/python.exe","webVis/simpleServer.py"])

    webbrowser.open("http://127.0.0.1:8000",2,True)