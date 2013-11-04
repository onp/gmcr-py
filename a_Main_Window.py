from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from data_01_conflictModel import ConflictModel
from frame_01_decisionMakers import DMInpFrame
from frame_02_infeasibles import InfeasInpFrame
from frame_03_irreversibles import IrrevInpFrame
from frame_04_preferences import PreferencesFrame
from frame_05_equilibria import ResultFrame
from frame_06_inverseApproach import InverseFrame

class MainAppWindow:
    def __init__(self,file=None):
        self.file = file
        
        self.root= Tk()
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

        self.saveButton   = ttk.Button(self.fileFrame,text='Save Game'   ,command=self.saveGame, width=20)
        self.saveAsButton = ttk.Button(self.fileFrame,text='Save Game As',command=self.saveAs,   width=20)
        self.loadButton   = ttk.Button(self.fileFrame,text='Load Game'   ,command=self.loadGame, width=20)
        self.newButton    = ttk.Button(self.fileFrame,text='New Game'    ,command=self.newGame,  width=20)

        self.saveButton.grid(  column=0, row=0, sticky=(E,W))
        self.saveAsButton.grid(column=0, row=1, sticky=(E,W))
        self.loadButton.grid(  column=0, row=2, sticky=(E,W))
        self.newButton.grid(   column=0, row=3, sticky=(E,W))

        if self.file is not None:
            self.activeGame = ConflictModel(file)
            self.root.wm_title(self.file)
        else:
            self.activeGame = ConflictModel()

        self.contentFrame.currFrame=1

        self.addMod(DMInpFrame)
        self.addMod(InfeasInpFrame)
        self.addMod(IrrevInpFrame)
        self.addMod(PreferencesFrame)
        self.addMod(ResultFrame)
        self.addMod(InverseFrame)

        self.frameBtnCmds[0](self)
        
        self.root.mainloop()

    def addMod(self,newMod):
        """ Adds a new input frame and Module to the Game """
        newFrame = newMod(self.contentFrame,self.activeGame)
        fNum = len(self.frameList)
        self.frameList.append(newFrame)


        def FSelect(self,*args):
            print('fselect '+str(newFrame.buttonLabel))
            self.frameLeave()
            newFrame.enter()
            self.contentFrame.currFrame=newFrame

        self.frameBtnCmds.append(FSelect)

        newButton = ttk.Button(self.pageSelectFrame,text=newFrame.buttonLabel,image=newFrame.bigIcon,compound="top",width=25,command=lambda: FSelect(self))
        self.frameBtnList.append(newButton)
        newButton.grid(column=len(self.frameBtnList),row=0,sticky=(N,S,E,W))

    def frameLeave(self):
        """ Ungrids the current frame and performs other exit tasks"""
        try:
            self.contentFrame.currFrame.leave()
            self.contentFrame.currFrame = None
        except AttributeError:
            pass

    def saveGame(self):
        """Saves all information to the currently active file."""
        if not self.file:
            self.saveAs()
            return
        self.contentFrame.currFrame.leave()
        self.contentFrame.currFrame.enter()
        self.activeGame.save_to_file(self.file)
        print('Saved')

    def saveAs(self):
        """Opens a file dialog that prompts for name and location for saving the game."""
        print(self.file)
        print('running saveAs')
        self.file = filedialog.asksaveasfilename(defaultextension= '.gmcr',
                                                filetypes = (("GMCRo Save Files", "*.gmcr")
                                                             ,("All files", "*.*") ),
                                                parent=self.root)
        self.root.wm_title(self.file)
        self.saveGame()


    def loadGame(self):
        """Opens a file dialog that prompts for a save file to open."""
        self.file = filedialog.askopenfilename(filetypes = (("GMCRo Save Files", "*.gmcr")
                                                             ,("All files", "*.*") ),
                                                parent=self.root)
        self.frameLeave()
        print('loading: %s'%(self.file))
        self.root.wm_title(self.file)
        self.activeGame.load_from_file(self.file)
        self.frameBtnCmds[0](self)
        

    def newGame(self):
        """Clears all data in the game, allowing a new game to be entered."""
        self.frameLeave()
        self.activeGame = ConflictModel()
        self.frameBtnCmds[0](self)
        self.root.wm_title('New GMCR Model')
    

if __name__ == '__main__':
    a= MainAppWindow()