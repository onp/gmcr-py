from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from subprocess import Popen, PIPE
import sys
import multiprocessing as mp

class MainWindow:

    def __init__(self):
    
        self.root = Tk()
        self.labelVar = StringVar()
        self.labelVar.set("start")
        self.label = ttk.Label(self.root,textvariable = self.labelVar )
        
        self.label.grid(column=0,row=0)
        
        self.root.mainloop()

        
        
def initApp():
    app = MainWindow()
    
def runProc():
    p = mp.Process(target=initApp)
    p.start()
    

if __name__ == '__main__':
    runProc()
    self.process = Popen([sys.executable], stdout=PIPE)

    