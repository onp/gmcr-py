# Template for input frames.  Shows the methods and attributes necessary for
#  interfacing with the main program

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel
from widgets_f04_01_prefRadioButton import RadiobuttonEntry
from widgets_f04_02_prefElements import *
import data_03_gmcrUtilities as gmcrUtil

class PreferencesFrame(ttk.Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master,game,*args):
        ttk.Frame.__init__(self,master,*args)
        
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        
        # Load up active game, if any
        self.game = game

        self.buttonLabel= 'Preferences'     #Label used for button to select frame in the main program.
        self.bigIcon=PhotoImage(file='icons/Preference.gif')         #Image used on button to select frame.
        
        self.built = False


# ############################     METHODS  #######################################

    def hasRequiredData(self):
        if len(self.game.decisionMakers) < 1:
            return False
        if len(self.game.options) < 1:
            return False
        if len(self.game.feasibles) < 1:
            return False
        else:
            return True
            
            
    def buildFrame(self):
        if self.built:
            return
        
        #calculate initial preferences
        for dm in self.game.decisionMakers:
            dm.calculatePreferences()
            
        #Define variables that will display in the infoFrame
        self.infoText = StringVar(value='Valid Preferences set for %s/%s DMs.'%(len(self.game.decisionMakers),len(self.game.decisionMakers)))

        #Define variables that will display in the helpFrame
        self.helpText = StringVar(value="Select a decision maker from the column at left by clicking its "
                "'View/Edit' button.  Enter preferred states using the box to the right.  Preferred "
                "states are shown below the decision makers, from most important at the top, to least "
                "important at the bottom")

        #Define frame-specific variables
        self.dm = self.game.decisionMakers[0]

        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.infoLabel  = ttk.Label(self.infoFrame,textvariable = self.infoText)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)

        #Define frame-specific input widgets (with 'self' or a child thereof as master)
        self.editor = RadiobuttonEntry(self,self.game)
        self.vectors = PreferenceRankingMaster(self,self.game)
        self.conditionDisp = PreferenceEditDisplay(self,self.game)
        self.prefDisp = PreferenceLongDisp(self,self.game)
        self.usePrioritizationButton = ttk.Button(self,
                text = "Use preference prioritization. Any manually set preference vectors will be lost.",
                command = self.usePrioritization)

        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0,row=0,rowspan=5,sticky=(N,S,E,W))
        self.grid_remove()

        #configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2,row=0,sticky=(N,S,E,W),padx=3,pady=3)
        self.infoFrame.grid_remove()
        self.infoLabel.grid(column=0,row=1,sticky=(N,S,E,W))

        #configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2,row=1,sticky=(N,S,E,W),padx=3,pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0,row=0,sticky=(N,S,E,W))

        #configuring frame-specific options
        self.vectors.grid(column=0,row=1,sticky=(N,S,E,W))
        self.conditionDisp.grid(column=0,row=2,sticky=(N,S,E,W))
        ttk.Separator(self,orient=VERTICAL).grid(column=1,row=1,rowspan=2,sticky=(N,S,E,W),padx=3)
        self.editor.grid(column=2,row=1,rowspan=2,sticky=(N,S,E,W))
        ttk.Separator(self,orient=VERTICAL).grid(column=3,row=1,rowspan=2,sticky=(N,S,E,W),padx=3)
        self.prefDisp.grid(column=4,row=1,rowspan=2,sticky=(N,S,E,W))
        self.columnconfigure(0,weight=1)
        self.columnconfigure(2,weight=0)
        self.columnconfigure(4,weight=2)
        self.rowconfigure(2,weight=1)

        # bindings
        self.vectors.bind('<<DMchg>>',self.dmChgHandler)
        self.editor.bind('<<AddPref>>',self.addPref)
        self.conditionDisp.bind('<<SelItem>>', self.selChg)
        self.conditionDisp.bind('<<ValueChange>>',self.refresh)
    
        self.built = True
        
    def clearFrame(self):
        if not self.built:
            return
        self.built = False
        for child in self.winfo_children():
            child.destroy()
        self.infoFrame.grid_forget()
        self.helpFrame.grid_forget()

    def enter(self,*args):
        """ Re-grids the main frame, infoFrame and helpFrame into the master,
        and performs any other update tasks required on loading the frame."""
        self.refresh()
        self.grid()
        self.infoFrame.grid()
        self.helpFrame.grid()

    def leave(self,*args):
        """ Removes the main frame, infoFrame and helpFrame from the master,
        and performs any other update tasks required on exiting the frame."""
        self.grid_remove()
        self.infoFrame.grid_remove()
        self.helpFrame.grid_remove()

    def refresh(self,*args):
        for dm in self.game.decisionMakers:
            dm.calculatePreferences()
        self.editor.reloadOpts()
        self.vectors.refresh()
        self.conditionDisp.refresh()
        self.prefDisp.refresh()
        
        if self.game.useManualPreferenceVectors:
            self.usePrioritizationButton.grid(column=0,row=0,columnspan=5,sticky=(N,S,E,W))
        else:
            self.usePrioritizationButton.grid_remove()
            
    def usePrioritization(self):
        self.game.useManualPreferenceVectors = False
        self.game.preferenceErrors = None
        self.event_generate("<<breakingChange>>")
        self.refresh()

    def dmChgHandler(self,event):
        """Bound to <<DMchg>>."""
        self.dm = self.vectors.dm
        self.conditionDisp.changeDM(self.dm)
        self.prefDisp.changeDM(self.dm)

    def addPref(self,*args):
        """Add a preference for the active decision maker."""
        pref = self.editor.getStates()
        self.dm.preferences.append(pref)
        self.refresh()

    def selChg(self,event):
        """Triggered when the selection changes in the treeview."""
        condition = self.dm.preferences[event.x]
        self.editor.setStates(condition.ynd())



# #################################################################################
# ###############                   TESTING                         ###############
# #################################################################################

# Code in this section is only run when this module is run by itself. It serves
# as a test of module functionality.

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

    testGame = ConflictModel('SyriaIraq.gmcr')

    testFrame = PreferencesFrame(cFrame,testGame)
    testFrame.enter()

    root.mainloop()

if __name__ == '__main__':
    main()