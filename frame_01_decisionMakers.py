# frame for inputting the dms and options.
# for future: consider implementing as paned window rather than frame.

from tkinter import *
from tkinter import ttk
from widgets_f01_01_editableListBox import ListInput
from data_01_conflictModel import ConflictModel


class DMInpFrame(ttk.Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master,game,*args):
        ttk.Frame.__init__(self,master,*args)

        # Connect to active game module
        self.game = game

        self.buttonLabel= 'Decision Makers and Options'     #Label used for button to select frame in the main program.
        self.bigIcon=PhotoImage(file='icons/DMs_OPs.gif')         #Image used on button to select frame.

        #Define variables that will display in the infoFrame
        self.dmCount  = StringVar(value='Number of Decision Makers: ' + 'init')
        self.optCount = StringVar(value='Number of Options: ' + 'init')
        self.stateCount = StringVar(value='Total States: ' + 'init')

        #Define variables that will display in the helpFrame
        self.helpText = StringVar(value='lots and lots of words about relevant stuff and instructions and so on and on and on and on and on.')

        #Define frame-specific variables
        self.optLabText = StringVar(value='')

        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.dmCountLabel  = ttk.Label(self.infoFrame,textvariable = self.dmCount)
        self.optCountLabel = ttk.Label(self.infoFrame,textvariable = self.optCount)
        self.stateCountLabel = ttk.Label(self.infoFrame,textvariable = self.stateCount)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)


        #Define frame-specific input widgets (with 'self' or a child therof as master)
        self.dmHSep1 = ttk.Separator(self,orient=VERTICAL)
        self.dmHSep2 = ttk.Separator(self,orient=VERTICAL)

        self.dmLabel1  = ttk.Label(self,text='Decision Makers')
        self.optLabel1 = ttk.Label(self,textvariable=self.optLabText)

        self.dmInp   = ListInput(self,lHeight=5)
        self.optsInp = ListInput(self)

        self.optPlaceholder = ttk.Label(self,text='Please Select a Decision Maker',anchor='center')


        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0,row=0,rowspan=5,sticky=(N,S,E,W))
        self.grid_remove()
        self.columnconfigure(0,weight=1)
        self.columnconfigure(2,weight=1)
        self.rowconfigure(4,weight=1)

        #configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2,row=0,sticky=(N,S,E,W),padx=3,pady=3)
        self.infoFrame.grid_remove()
        self.dmCountLabel.grid(column=0, row=1,sticky=(N,S,E,W))
        self.optCountLabel.grid(column=0, row=2,sticky=(N,S,E,W))
        self.stateCountLabel.grid(column=0,row=3,sticky=(N,S,E,W))

        #configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2,row=1,sticky=(N,S,E,W),padx=3,pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0,row=0,sticky=(N,S,E,W))

        #configuring frame-specific options
        self.dmHSep1.grid(column=1,row=0,rowspan=10,sticky=(N,S,E,W))

        self.dmLabel1.grid(column=0,row=1,sticky=(N,S,E,W))
        self.optLabel1.grid(column=2,row=1,sticky=(N,S,E,W))

        self.dmInp.grid(column=0,row=2,rowspan=5,sticky=(N,S,E,W))
        self.optsInp.grid(column=2,row=2,rowspan=5,sticky=(N,S,E,W))
        self.optPlaceholder.grid(column=2,row=2,rowspan=5,sticky=(N,S,E,W))


        # bindings
        self.dmInp.bind('<<Sel2>>', self.dmChange)
        self.dmInp.bind('<<Chg>>',  self.updateTotals)
        self.optsInp.bind('<<Chg>>',self.updateTotals)


# ############################     METHODS  #######################################

    def refreshWidgets(self):
        self.dmInp.linkVar(self.game.dmList,self.game.optList)
        self.oldVals = str([self.game.dmList,self.game.optList])
        self.updateTotals()

    def enter(self,*args):
        """ Re-grids the main frame, infoFrame and helpFrame into the master,
        and performs any other update tasks required on loading the frame."""
        self.refreshWidgets()
        self.grid()
        self.infoFrame.grid()
        self.helpFrame.grid()

    def leave(self,*args):
        """ Removes the main frame, infoFrame and helpFrame from the master,
        and performs any other update tasks required on exiting the frame."""
        self.optsInp.grid_remove()
        self.optPlaceholder.grid()
        self.grid_remove()
        self.infoFrame.grid_remove()
        self.helpFrame.grid_remove()
        if self.oldVals != str([self.game.dmList,self.game.optList]):
            self.game.setOpts(self.game.optList)
            self.game.setDMs(self.game.dmList)
            self.game.setInfeas([])


    def dmChange(self,*args):
        idx = int(self.dmInp.listDisp.curselection()[0])
        if idx != len(self.game.dmList):
            self.optLabText.set('Options for '+self.game.dmList[idx])
            self.optPlaceholder.grid_remove()
            self.optsInp.linkVar(self.game.optList[idx])
            self.optsInp.grid()
        else:
            self.optsInp.grid_remove()
            self.optLabText.set('')
            self.optPlaceholder.grid()



    def updateTotals(self,*args):
        self.dmCount.set('Number of Decision Makers: ' + str(len(self.game.dmList)))
        self.optCount.set('Number of Options: ' + str(sum([len(x) for x in self.game.optList])))
        self.stateCount.set('Total States: ' + str(2**sum([len(x) for x in self.game.optList])))




# ######################

def main():

    root = Tk()
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)

    cFrame = ttk.Frame(root)
    cFrame.columnconfigure(0,weight=1)
    cFrame.rowconfigure(1,weight=1)
    cFrame.grid(column=0,row=0,sticky=(N,S,E,W))

    hSep = ttk.Separator(cFrame,orient=VERTICAL)
    hSep.grid(column=1,row=0,rowspan=10,sticky=(N,S,E,W))

    g1 = ConflictModel('AmRv2.gmcr')

    testFrame = DMInpFrame(cFrame,g1)
    testFrame.enter()

    root.mainloop()

if __name__ == '__main__':
    main()