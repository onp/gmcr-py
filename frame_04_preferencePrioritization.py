# Copyright:   (c) Oskar Petersons 2013

"""Frame used to set decision maker's preferences for use in prioritization.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import *
from tkinter import ttk
from widgets_f04_01_prefRadioButton import RadiobuttonEntry
from widgets_f04_02_prefElements import *
from widgets_f04_03_optionForm import OptionFormTable
import data_03_gmcrUtilities as gmcrUtil

class PreferencesFrame(ttk.Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master,game,*args):
        ttk.Frame.__init__(self,master,*args)
        
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        
        # Load up active game, if any
        self.game = game

        self.buttonLabel= 'Prioritization'     #Label used for button to select frame in the main program.
        self.activeIcon = PhotoImage(file='icons/Prioritization_ON.gif')      #Image used on button to select frame, when frame is active.
        self.inactiveIcon = PhotoImage(file='icons/Prioritization_OFF.gif')    #Image used on button to select frame, when frame is inactive.
        
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
        self.helpText = StringVar(value=""
                "Select a decision maker from the column at left by clicking its "
                "'Edit' button.  Enter preferred conditions using the inputs to "
                "the right.  Preferred conditions for the selected decision maker "
                "are shown at the far right, from most important at the top, to "
                "least important at the bottom.")

        #Define frame-specific variables
        self.dm = None

        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.infoLabel  = ttk.Label(self.infoFrame,textvariable = self.infoText)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)

        #Define frame-specific input widgets (with 'self' or a child thereof as master)
        self.paneMaster = PanedWindow(self,orient=VERTICAL,sashwidth=5,sashrelief="raised",sashpad=2,relief="sunken")
        
        self.paneTop = ttk.Frame(self.paneMaster)
        self.vectors = PreferenceRankingMaster(self.paneTop,self.game)
        self.editor = RadiobuttonEntry(self.paneTop,self.game)
        self.staging = PreferenceStaging(self.paneTop,self.game)
        self.preferenceDisp = PreferenceListDisplay(self.paneTop,self.game)
        
        self.paneBottom = ttk.Frame(self.paneMaster)
        self.optionTable = OptionFormTable(self.paneBottom,self.game)
        
        self.usePrioritizationButton = ttk.Button(self,
                text = "Use preference prioritization. Any manually set preference vectors will be lost.",
                command = self.usePrioritization)

        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0,row=0,rowspan=5,sticky=(N,S,E,W))
        self.columnconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
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
        self.paneMaster.grid(column=0,row=1,sticky=(N,S,E,W))
        self.paneMaster.add(self.paneTop)
        self.vectors.grid(column=0,row=1,sticky=(N,S,E,W))
        ttk.Separator(self.paneTop,orient=VERTICAL).grid(column=1,row=1,sticky=(N,S,E,W),padx=3)
        self.editor.grid(column=2,row=1,sticky=(N,S,E,W))
        ttk.Separator(self.paneTop,orient=VERTICAL).grid(column=3,row=1,sticky=(N,S,E,W),padx=3)
        self.staging.grid(column=4,row=1,sticky=(N,S,E,W))
        ttk.Separator(self.paneTop,orient=VERTICAL).grid(column=5,row=1,sticky=(N,S,E,W),padx=3)
        self.preferenceDisp.grid(column=6,row=1,sticky=(N,S,E,W))
        self.paneTop.columnconfigure(0,weight=1)
        self.paneTop.columnconfigure(2,weight=0)
        self.paneTop.columnconfigure(4,weight=1)       
        self.paneTop.columnconfigure(6,weight=1)
        self.paneTop.rowconfigure(1,weight=1)
        
        self.paneMaster.add(self.paneBottom)
        self.optionTable.grid(column=0,row=0,sticky=(N,S,E,W))
        self.paneBottom.columnconfigure(0,weight=1)
        self.paneBottom.rowconfigure(0,weight=1)

        # bindings
        self.vectors.bind('<<DMchg>>',self.dmChgHandler)
        self.editor.bind('<<AddPref>>',self.addPref)
        self.editor.bind('<<StagePref>>',self.stagePref)
        self.staging.bind('<<SelCond>>', self.selCondChg)
        self.staging.bind('<<PullFromStage>>',self.pullFromStage)
        self.preferenceDisp.bind('<<SelPref>>', self.selPrefChg)
        self.preferenceDisp.bind('<<ValueChange>>',self.refresh)
        
        self.dmChgHandler()
    
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
        if not self.built:
            self.buildFrame()
        self.refresh()
        self.grid()
        self.infoFrame.grid()
        self.helpFrame.grid()
        if self.button:
            self.button['image'] = self.activeIcon

    def leave(self,*args):
        """ Removes the main frame, infoFrame and helpFrame from the master,
        and performs any other update tasks required on exiting the frame."""
        self.grid_remove()
        self.infoFrame.grid_remove()
        self.helpFrame.grid_remove()
        if self.button:
            self.button['image'] = self.inactiveIcon

    def refresh(self,*args):
        for dm in self.game.decisionMakers:
            dm.calculatePreferences()
        self.editor.reloadOpts()
        self.vectors.refresh()
        self.preferenceDisp.refresh()
        self.optionTable.buildTable(self.dm)
        
        if self.game.useManualPreferenceVectors:
            self.usePrioritizationButton.grid(column=0,row=0,columnspan=5,sticky=(N,S,E,W))
            self.vectors.disable()
            self.editor.disable()
            self.staging.disable()
            self.preferenceDisp.disable()
        else:
            self.usePrioritizationButton.grid_remove()
            
    def usePrioritization(self):
        self.game.useManualPreferenceVectors = False
        self.game.preferenceErrors = None
        self.event_generate("<<breakingChange>>")
        self.vectors.enable()
        self.refresh()

    def dmChgHandler(self,event=None):
        """Bound to <<DMchg>>."""
        self.dm = self.vectors.dm
        self.preferenceDisp.changeDM(self.dm)
        self.optionTable.buildTable(self.dm)
        self.staging.clear()
        self.editor.setStates('clear')
        if self.dm is None:
            self.preferenceDisp.disable()
            self.editor.disable()
            self.staging.disable()
        else:
            self.preferenceDisp.enable()
            self.editor.enable()

    def addPref(self,event=None):
        """Add a preference for the active decision maker."""
        pref = self.editor.getStates()
        self.dm.preferences.append(pref)
        self.refresh()
        
    def stagePref(self,event=None):
        """Stages a condition."""
        condData = self.editor.getStates()
        newCond = self.game.newCondition(condData)
        self.staging.addCondition(newCond)
        self.editor.setStates('clear')

    def pullFromStage(self,event=None):
        """Moves a compound condition from Staging to Preferences."""
        newPref = self.staging.conditionList
        self.staging.clear()
        self.dm.preferences.append(newPref)
        self.refresh()
        
    def selCondChg(self,event=None):
        """Triggered when a condition is selected in staging."""
        condition = self.staging.conditionList[event.x]
        self.editor.setStates(condition.ynd())
        
    def selPrefChg(self,event=None):
        """Triggered when a preference is select from preferences."""
        condition = self.dm.preferences[event.x]
        self.staging.setList(condition)



# #################################################################################
# ###############                   TESTING                         ###############
# #################################################################################

# Code in this section is only run when this module is run by itself. It serves
# as a test of module functionality.


def main():
    from data_01_conflictModel import ConflictModel
    
    root = Tk()
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)

    cFrame = ttk.Frame(root)
    cFrame.columnconfigure(0,weight=1)
    cFrame.rowconfigure(1,weight=1)
    cFrame.grid(column=0,row=0,sticky=(N,S,E,W))

    hSep = ttk.Separator(cFrame,orient=VERTICAL)
    hSep.grid(column=1,row=0,rowspan=10,sticky=(N,S,E,W))

    conf = ConflictModel()
    conf.load_from_file("save_files/Garrison.gmcr")

    testFrame = PreferencesFrame(cFrame,conf)
    if testFrame.hasRequiredData():
        testFrame.buildFrame()
    else:
        print("data missing")
        return
    testFrame.enter()



    root.mainloop()

if __name__ == '__main__':
    main()