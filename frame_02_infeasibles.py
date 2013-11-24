# Copyright:   (c) Oskar Petersons 2013

"""Frame for editing infeasible states in the conflict.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import *
from tkinter import ttk
from widgets_f02_01_radioButtonEntry import RadiobuttonEntry
from widgets_f02_02_infeasTreeview import TreeInfeas
from widgets_f02_03_feasDisp import FeasDisp
from data_01_conflictModel import ConflictModel
import data_03_gmcrUtilities as gmcrUtil

class InfeasInpFrame(Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master,game,*args):
        ttk.Frame.__init__(self,master,*args)
        
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')

        # Connect to active game module
        self.game = game

        self.buttonLabel= 'Infeasible States'               #Label used for button to select frame in the main program.
        self.bigIcon=PhotoImage(file='icons/Infeasible.gif')         #Image used on button to select frame.

        self.built = False



# ############################     METHODS  #######################################

    def hasRequiredData(self):
        if len(self.game.decisionMakers) < 1:
            return False
        if len(self.game.options) < 1:
            return False
        else:
            return True
            
    def buildFrame(self):
        if self.built:
            return
        #Define variables that will display in the infoFrame
        self.originalStatesText = StringVar(value='Original States: '+'init')
        self.removedStatesText = StringVar(value='States Removed: '+'init')
        self.feasStatesText = StringVar(value='States Remaining: '+'init')

        #Define variables that will display in the helpFrame
        self.helpText = StringVar(value="Enter infeasible states using the box at left. Removing as infeasible "
                "state will remove all states that match the pattern from the game. Removing as mutually "
                "exclusive will remove all states where ANY TWO OR MORE of the specified options occur together.")

        #Define frame-specific variables
        self.warnText = StringVar(value='')

        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.originalStatesLabel  = ttk.Label(self.infoFrame,textvariable = self.originalStatesText)
        self.removedStatesLabel  = ttk.Label(self.infoFrame,textvariable = self.removedStatesText)
        self.feasStatesLabel  = ttk.Label(self.infoFrame,textvariable = self.feasStatesText)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)

        #Define frame-specific input widgets (with 'self' as master)
        self.optsFrame = ttk.Frame(self)
        self.hSep = ttk.Separator(self,orient=VERTICAL)
        self.infeasFrame = ttk.Panedwindow(self,orient=HORIZONTAL)

        self.optsInp    = RadiobuttonEntry(self.optsFrame,self.game)
        self.infeasDisp = TreeInfeas(self.infeasFrame,self.game)
        self.feasList   = FeasDisp(self.infeasFrame,self.game)
        self.infeasFrame.add(self.infeasDisp)
        self.infeasFrame.add(self.feasList)

        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0,row=0,rowspan=5,sticky=(N,S,E,W))
        self.grid_remove()

        self.columnconfigure(2,weight=3)
        self.rowconfigure(0,weight=1)

        #configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2,row=0,sticky=(N,S,E,W),padx=3,pady=3)
        self.infoFrame.grid_remove()
        self.originalStatesLabel.grid(column=0,row=1,sticky=(N,S,E,W))
        self.removedStatesLabel.grid(column=0,row=2,sticky=(N,S,E,W))
        self.feasStatesLabel.grid(column=0,row=3,sticky=(N,S,E,W))

        #configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2,row=1,sticky=(N,S,E,W),padx=3,pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0,row=0,sticky=(N,S,E,W))


        #configuring frame-specific options
        self.optsFrame.columnconfigure(0,weight=1)
        self.optsFrame.rowconfigure(0,weight=1)
        self.optsFrame.grid(column=0,row=0,sticky=(N,S,E,W))

        self.infeasFrame.grid(column=2,row=0,sticky=(N,S,E,W))

        self.optsInp.grid(column=0,row=0,columnspan=2,sticky=(N,S,E,W))
        self.optsInp.bind('<<AddInfeas>>',self.addInfeas)
        self.optsInp.bind('<<AddMutEx>>', self.addMutEx)

        self.infeasDisp.bind('<<SelItem>>', self.selChg)
        self.infeasDisp.bind('<<ValueChange>>',self.refreshWidgets)

        self.hSep.grid(column=1,row=0,rowspan=10,sticky=(N,S,E,W))

        self.refreshWidgets()
        
        self.built = True
            
    def clearFrame(self):
        if not self.built:
            return
        self.built = False
        for child in self.winfo_children():
            child.destroy()
        self.infoFrame.grid_forget()
        self.helpFrame.grid_forget()

    def refreshWidgets(self,*args):
        """Refresh information in the widgets.  Triggered when information changes."""
        self.infeasDisp.refreshView()
        self.feasList.refreshList()
        self.originalStatesText.set('Original States: %s' %(2**len(self.game.options)))
        self.feasStatesText.set('Feasible States: %s'%(len(self.game.feasibles)))
        self.removedStatesText.set('States Removed: %s'%(2**len(self.game.options) - len(self.game.feasibles)))

    def addInfeas(self,*args):
        """Remove an infeasible state from the game."""
        infeas = self.optsInp.getStates()
        self.game.infeasibles.append(infeas)
        self.game.recalculateFeasibleStates()
        self.refreshWidgets()

    def addMutEx(self,*args):
        """Remove a set of Mutually Exclusive States from the game."""
        mutEx = self.optsInp.getStates()
        mutEx = gmcrUtil.mutuallyExclusive(mutEx)
        print(mutEx)
        print(mutEx[0])
        for infeas in mutEx:
            self.game.infeasibles.append(list(infeas))
        self.refreshWidgets()

    def selChg(self,event):
        """Triggered when the selection changes in the treeview."""
        state = self.game.infeasibles[event.x].ynd()
        self.optsInp.setStates(state)

    def enter(self):
        """Run when entering the Infeasible States screen."""
        self.refreshWidgets()
        self.grid()
        self.infoFrame.grid()
        self.helpFrame.grid()
        self.optsInp.reloadOpts()

    def leave(self):
        """Run when leaving the Infeasible States screen."""
        self.grid_remove()
        self.infoFrame.grid_remove()
        self.helpFrame.grid_remove()



# ########

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

    g1 = ConflictModel('Prisoners.gmcr')

    testFrame = InfeasInpFrame(cFrame,g1)
    testFrame.enter()

    root.mainloop()


if __name__ == '__main__':
    main()
