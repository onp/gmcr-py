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
    def __init__(self,master,conflict,*args):
        ttk.Frame.__init__(self,master,*args)
        
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        
        # Load up active conflict, if any
        self.conflict = conflict

        self.buttonLabel= 'Prioritization'     #Label used for button to select frame in the main program.
        self.activeIcon = PhotoImage(file='icons/Prioritization_ON.gif')      #Image used on button to select frame, when frame is active.
        self.inactiveIcon = PhotoImage(file='icons/Prioritization_OFF.gif')    #Image used on button to select frame, when frame is inactive.
        
        self.built = False
        
        self.lastBuildDMs = None
        self.lastBuildOptions = None
        self.lastBuildInfeasibles = None


# ############################     METHODS  #######################################

    def hasRequiredData(self):
        if len(self.conflict.decisionMakers) < 1:
            return False
        if len(self.conflict.options) < 1:
            return False
        if len(self.conflict.feasibles) < 1:
            self.conflict.recalculateFeasibleStates()
            if len(self.conflict.feasibles) < 1:
                return False
        else:
            return True
            
    def dataChanged(self):
        if self.lastBuildDMs != self.conflict.decisionMakers.export_rep():
            return True
        if self.lastBuildOptions != self.conflict.options.export_rep():
            return True
        if self.lastBuildInfeasibles != self.conflict.infeasibles.export_rep():
            return True
        else:
            return False
            
        
            
    def buildFrame(self):
        if self.built:
            return
        
        # Ensure all required parts of the conflict model are properly set-up.
        self.conflict.reorderOptionsByDM()
        self.conflict.options.set_indexes()
        self.conflict.infeasibles.validate()
        self.conflict.recalculateFeasibleStates()
        
        for dm in self.conflict.decisionMakers:
            dm.calculatePreferences()
        
        self.lastBuildDMs = self.conflict.decisionMakers.export_rep()
        self.lastBuildOptions = self.conflict.options.export_rep()
        self.lastBuildInfeasibles = self.conflict.infeasibles.export_rep()
        
            
        #Define variables that will display in the infoFrame
        self.infoText = StringVar(value='Valid Preferences set for %s/%s DMs.'%(len(self.conflict.decisionMakers),len(self.conflict.decisionMakers)))

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
        self.rankings = PreferenceRankingMaster(self.paneTop,self.conflict)
        self.editor = RadiobuttonEntry(self.paneTop,self.conflict)
        self.paneTopRightMaster = PanedWindow(self.paneTop,orient=HORIZONTAL,sashwidth=5,sashrelief="raised",sashpad=2,relief="sunken")
        self.staging = PreferenceStaging(self.paneTopRightMaster,self.conflict)
        self.preferenceDisp = PreferenceListDisplay(self.paneTopRightMaster,self.conflict)
        
        self.paneBottom = ttk.Frame(self.paneMaster)
        self.optionTable = OptionFormTable(self.paneBottom,self.conflict)
        
        self.usePrioritizationButton = ttk.Button(self,
                text = "Use preference prioritization. Any manually set preference rankings will be lost.",
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
        self.paneMaster.add(self.paneTop,minsize=200)
        self.rankings.grid(column=0,row=1,sticky=(N,S,E,W))
        ttk.Separator(self.paneTop,orient=VERTICAL).grid(column=1,row=1,sticky=(N,S,E,W),padx=3)
        self.editor.grid(column=2,row=1,sticky=(N,S,E,W))
        ttk.Separator(self.paneTop,orient=VERTICAL).grid(column=3,row=1,sticky=(N,S,E,W),padx=3)
        self.paneTopRightMaster.grid(column=4,row=1,sticky=(N,S,E,W))
        self.paneTop.columnconfigure(0,weight=0)
        self.paneTop.columnconfigure(2,weight=0)
        self.paneTop.columnconfigure(4,weight=1)
        self.paneTop.rowconfigure(1,weight=1)
        
        self.usePrioritizationButton.grid(column=0,row=0,columnspan=5,sticky=(N,S,E,W))
        

        self.paneTopRightMaster.add(self.staging)
        self.paneTopRightMaster.add(self.preferenceDisp)
        
        self.paneMaster.add(self.paneBottom)
        self.optionTable.grid(column=0,row=0,sticky=(N,S,E,W))
        self.paneBottom.columnconfigure(0,weight=1)
        self.paneBottom.rowconfigure(0,weight=1)

        # bindings
        self.rankings.bind('<<DMchg>>',self.dmChgHandler)
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
        
        if self.dataChanged():
            self.clearFrame()
        
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
        for dm in self.conflict.decisionMakers:
            dm.calculatePreferences()
        self.editor.reloadOpts()
        self.rankings.refresh()
        self.preferenceDisp.refresh()
        self.optionTable.buildTable(self.dm)
        
        self.checkIfUsingRankings()
        
    def checkIfUsingRankings(self,event=None):
        if self.conflict.useManualPreferenceRanking:
            self.usePrioritizationButton.grid()
            self.rankings.disable()
            self.editor.disable()
            self.staging.disable()
            self.preferenceDisp.disable()
        else:
            self.usePrioritizationButton.grid_remove()
            
    def usePrioritization(self):
        self.conflict.useManualPreferenceRanking = False
        self.conflict.preferenceErrors = None
        self.refresh()

    def dmChgHandler(self,event=None):
        """Bound to <<DMchg>>."""
        self.dm = self.rankings.dm
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
        if self.editor.hasValidIf:
            for cond in self.editor.ifCond:
                self.staging.addCondition(cond)
        else:
            condData = self.editor.getStates()
            newCond = self.conflict.newCondition(condData)
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