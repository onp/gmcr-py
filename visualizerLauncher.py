import webbrowser
import sys
from multiprocessing import Process
import http.server
import os


class Fakestd(object):
    def write(self, string):
        pass

    def flush(self):
        pass


def serve():
    # required to successfully freeze multiprocessing to a win32gui application
    sys.stderr = Fakestd()
    sys.stdout = Fakestd()
    
    #move to the temp folder where the visualizer files were copied
    os.chdir(os.environ['TEMP'] + '/gmcr-vis')

    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("",PORT),Handler)
    print("now serving on port ", PORT)
    httpd.serve_forever()

    
    
def launchVis(data=None):
    serverThread = Process(target=serve,daemon=True)

    serverThread.start()

    webbrowser.open("http://127.0.0.1:8000",2,True)