# Copyright:   (c) Oskar Petersons 2013

"""Launches the GMCR-py Decision Support System."""

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from data_01_conflictModel import ConflictModel
from frame_01_decisionMakers import DMInpFrame
from frame_02_infeasibles import InfeasInpFrame
from frame_03_irreversibles import IrrevInpFrame
from frame_04_preferencePrioritization import PreferencesFrame
from frame_05_preferenceRanking import PreferenceRankingFrame
from frame_06_equilibria import ResultFrame
from frame_07_inverseGMCR import InverseFrame
from frame_08_stabilityAnalysis import StabilityFrame

from multiprocessing import freeze_support
import os

class MainAppWindow:
    def __init__(self,file=None):
        self.file = file # file reference used for saving the conflict.

        self.root= Tk()
        self.root.iconbitmap('gmcr.ico')
        self.root.wm_title('New GMCR+ Model')
        self.root.columnconfigure(0,weight=1)
        self.root.rowconfigure(0,weight=1)

        self.frameList    = []
        self.frameBtnCmds = []
        self.frameBtnList = []

        self.topFrame = ttk.Frame(self.root)
        self.fileFrame = ttk.Frame(self.topFrame,border=3,relief='raised')
        self.pageSelectFrame = ttk.Frame(self.topFrame,border=3,relief='raised')
        self.contentFrame = ttk.Frame(self.topFrame)
        self.topVSep = ttk.Separator(self.topFrame,orient=HORIZONTAL)
        self.bottomHSep = ttk.Separator(self.contentFrame,orient=VERTICAL)

        self.topFrame.grid(column=0,row=0,sticky=(N,S,E,W))
        self.topFrame.columnconfigure(2,weight=1)
        self.topFrame.rowconfigure(3,weight=1)
        self.fileFrame.grid(column=0,row=1,sticky=(N,S,E,W))
        self.pageSelectFrame.grid(column=1,row=1,columnspan=4,sticky=(N,S,W))
        self.pageSelectFrame.rowconfigure(0,weight=1)
        self.topVSep.grid(column=0,row=2,columnspan=10,sticky=(N,S,E,W))
        self.bottomHSep.grid(column=1,row=0,rowspan=10,sticky=(N,S,E,W))
        self.contentFrame.grid(column=0,row=3,columnspan=5,sticky=(N,S,E,W))
        self.contentFrame.columnconfigure(0,weight=1)
        self.contentFrame.rowconfigure(1,weight=1)

        self.saveButton   = ttk.Button(self.fileFrame,text='Save Conflict'   ,command=self.saveConflict, width=20)
        self.saveAsButton = ttk.Button(self.fileFrame,text='Save Conflict As',command=self.saveAs,   width=20)
        self.loadButton   = ttk.Button(self.fileFrame,text='Load Conflict'   ,command=self.loadConflict, width=20)
        self.newButton    = ttk.Button(self.fileFrame,text='New Conflict'    ,command=self.newConflict,  width=20)

        self.saveButton.grid(  column=0, row=0, sticky=(E,W))
        self.saveAsButton.grid(column=0, row=1, sticky=(E,W))
        self.loadButton.grid(  column=0, row=2, sticky=(E,W))
        self.newButton.grid(   column=0, row=3, sticky=(E,W))

        self.activeConflict = ConflictModel()

        self.contentFrame.currFrame=None

        self.addMod(DMInpFrame)
        self.addMod(InfeasInpFrame)
        self.addMod(IrrevInpFrame)
        self.addMod(PreferencesFrame)
        self.addMod(PreferenceRankingFrame)
        self.addMod(ResultFrame)
        self.addMod(InverseFrame)
        self.addMod(StabilityFrame)

        self.refreshActiveFrames()

        self.root.bind_all("<<checkData>>",self.checkFramesHaveData)

        if self.file is not None:
            self.loadConflict(self.file)

        self.root.mainloop()

    def addMod(self,newMod):
        """ Adds a new input frame and Module to the Conflict """
        newFrame = newMod(self.contentFrame,self.activeConflict)
        fNum = len(self.frameList)
        self.frameList.append(newFrame)

        def FSelect(self,*args):
            print('Loading %s frame...'%(str(newFrame.buttonLabel)))
            self.frameLeave()
            newFrame.enter()
            self.contentFrame.currFrame=newFrame

        self.frameBtnCmds.append(FSelect)

        newButton = ttk.Button(self.pageSelectFrame,text=newFrame.buttonLabel,image=newFrame.inactiveIcon,compound="top",width=20,command=lambda: FSelect(self))
        self.frameBtnList.append(newButton)
        newFrame.button = newButton
        newButton.grid(column=len(self.frameBtnList),row=0,sticky=(N,S,E,W))

    def checkFramesHaveData(self,event=None):
        for idx,frame in enumerate(self.frameList):
            if frame.hasRequiredData():
                self.frameBtnList[idx].config(state = "normal")
            else:
                frame.clearFrame()
                self.frameBtnList[idx].config(state = "disabled")
            if frame != self.contentFrame.currFrame:
                frame.built = False

    def refreshActiveFrames(self,event=None):
        self.unloadAllFrames()
        self.checkFramesHaveData()

        try:
            self.contentFrame.currFrame.built = False
        except AttributeError:
            pass

        try:
            if self.contentFrame.currFrame.hasRequiredData():
                self.contentFrame.currFrame.enter()
            else:
                self.frameBtnCmds[0](self)
        except AttributeError:
            self.frameBtnCmds[0](self)

    def unloadAllFrames(self,event=None):
        for idx,frame in enumerate(self.frameList):
            frame.clearFrame()
            self.frameBtnList[idx].config(state = "disabled")



    def frameLeave(self):
        """ Ungrids the current frame and performs other exit tasks"""
        try:
            self.contentFrame.currFrame.leave()
        except AttributeError:
            pass

    def saveConflict(self):
        """Saves all information to the currently active file."""
        if not self.file:
            self.saveAs()
            return
        try:
            self.contentFrame.currFrame.leave()
        except AttributeError:
            pass
        self.contentFrame.currFrame.enter()
        self.activeConflict.save_to_file(self.file)
        print('Saved')

    def saveAs(self):
        """Opens a file dialog that prompts for name and location for saving the conflict."""
        print('running saveAs')
        fileName = filedialog.asksaveasfilename(defaultextension= '.gmcr',
                                                filetypes = (("GMCR+ Save Files", "*.gmcr")
                                                             ,("All files", "*.*") ),
                                                parent=self.root)
        if fileName:
            self.file = fileName
            self.root.wm_title(self.file)
            self.saveConflict()


    def loadConflict(self,fileName=None):
        """Opens a file dialog that prompts for a save file to open."""
        if not fileName:
            fileName = filedialog.askopenfilename(filetypes = (("GMCR+ Save Files", "*.gmcr"),
                                                                ("All files", "*.*") ),
                                                initialdir= os.getcwd()+'/Examples',
                                                parent=self.root)
        if fileName:
            self.file=fileName
            self.frameBtnCmds[0](self)
            self.frameLeave()
            self.unloadAllFrames()
            print('loading: %s'%(fileName))
            self.root.wm_title(fileName)
            self.activeConflict.load_from_file(fileName)
            self.refreshActiveFrames()


    def newConflict(self):
        """Clears all data in the conflict, allowing a new conflict to be entered."""
        print("Initializing new conflict...")
        self.unloadAllFrames()
        self.activeConflict.__init__()
        self.file = None
        self.refreshActiveFrames()
        self.root.wm_title('New GMCR+ Model')


if __name__ == '__main__':
    freeze_support()
    os.chdir(sys.argv[0].rpartition('\\')[0])
    launchFile= None
    try:
        launchFile = sys.argv[1]
    except IndexError:
        pass
    a= MainAppWindow(launchFile)
