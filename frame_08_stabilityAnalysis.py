# Copyright:   (c) Oskar Petersons 2013

"""Frame used to for Stability Analysis.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import *
from tkinter import ttk
from data_02_conflictSolvers import GoalSeeker
from widgets_f06_01_logResultDisp import CoalitionSelector
from widgets_f04_03_optionForm import OptionFormTable
from widgets_f08_01_stabilityAnalysis import *




class StabilityFrame(ttk.Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master,conflict,*args):
        ttk.Frame.__init__(self,master,*args)
        
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')

        self.conflict = conflict

        self.buttonLabel= 'Post Analysis'     #Label used for button to select frame in the main program.
        self.activeIcon = PhotoImage(file='icons/Post_Analysis_ON.gif')      #Image used on button to select frame, when frame is active.
        self.inactiveIcon = PhotoImage(file='icons/Post_Analysis_OFF.gif')    #Image used on button to select frame, when frame is inactive.

        
        self.built = False
        
        self.lastBuildConflict = None


# ############################     METHODS  #######################################

    def hasRequiredData(self):
        if len(self.conflict.decisionMakers) < 1:
            return False
        if len(self.conflict.options) < 1:
            return False
        if len(self.conflict.feasibles) < 1:
            return False
        if self.conflict.preferenceErrors:
            return False
        else:
            return True
            
    def dataChanged(self):
        if self.lastBuildConflict != self.conflict.export_rep():
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
        
        self.lastBuildConflict = self.conflict.export_rep()
        #Define variables that will display in the infoFrame
        self.infoText = StringVar(value="")

        #Define variables that will display in the helpFrame
        self.helpText = StringVar(value=""
        "Selecting coalitions, status quo and goals at the top left will "
        "generate a reachability tree below the status quo, and detail "
        "the patterns that preferences must match for the goal state to be "
        "reached.")

        #Define frame-specific variables
        self.sol = GoalSeeker(self.conflict)

        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.infoLabel  = ttk.Label(self.infoFrame,textvariable = self.infoText)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)

        #Define frame-specific input widgets (with 'self' or a child thereof as master)
        self.paneMaster  = PanedWindow(self,orient=HORIZONTAL,sashwidth=10,sashrelief="raised",sashpad=3,relief="sunken")
        
        self.paneLeft = PanedWindow(self.paneMaster,orient=VERTICAL,sashwidth=10,sashrelief="raised",sashpad=3,relief="sunken")
        
        self.paneLeftTop = ttk.Frame(self.paneLeft)
        self.coalitionSelector = CoalitionSelector(self.paneLeftTop,self.conflict,self)
        self.statusQuoAndGoals = StatusQuoAndGoals(self.paneLeftTop,self.conflict)
        self.reachableTree = ReachableTreeViewer(self.paneLeftTop,self.conflict,self)
        
        self.paneLeftBottom = ttk.Frame(self.paneLeft)
        self.optionFormTable = OptionFormTable(self.paneLeftBottom,self.conflict)
        
        self.paneRight = ttk.Frame(self.paneMaster)
        self.patternNarrator = PatternNarrator(self.paneRight,self.conflict,self)

        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0,row=0,rowspan=5,sticky=(N,S,E,W))
        self.grid_remove()
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)

        #configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2,row=0,sticky=(N,S,E,W),padx=3,pady=3)
        self.infoFrame.grid_remove()
        self.infoLabel.grid(column=0,row=1,sticky=(N,S,E,W))

        #configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2,row=1,sticky=(N,S,E,W),padx=3,pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0,row=0,sticky=(N,S,E,W))

        #configuring frame-specific options
        self.paneMaster.grid(row=0,column=0,sticky=(N,S,E,W))
        
        self.paneMaster.add(self.paneLeft)
        
        self.paneLeft.add(self.paneLeftTop)
        self.paneLeftTop.columnconfigure(1,weight=1)
        self.paneLeftTop.rowconfigure(2,weight=1)
        self.coalitionSelector.grid(row=0,column=0,sticky=(N,S,E,W))
        ttk.Separator(self,orient=HORIZONTAL).grid(row=1,column=0,sticky=(N,S,E,W),pady=3)
        self.statusQuoAndGoals.grid(row=2,column=0,sticky=(N,S,E,W))
        self.reachableTree.grid(row=0,column=1,rowspan=3,sticky=(N,S,E,W))
        
        self.paneLeft.add(self.paneLeftBottom)
        self.paneLeftBottom.rowconfigure(0,weight=1)
        self.paneLeftBottom.columnconfigure(0,weight=1)
        self.optionFormTable.grid(row=0,column=0,sticky=(N,S,E,W))
        
        self.paneMaster.add(self.paneRight)
        self.paneRight.rowconfigure(0,weight=1)
        self.paneRight.columnconfigure(0,weight=1)
        self.patternNarrator.grid(row=0,column=0,sticky=(N,S,E,W))

        # bindings
        self.statusQuoAndGoals.bind("<<StatusQuoChanged>>",self.statusQuoGoalChange)
        self.statusQuoAndGoals.bind("<<GoalChanged>>",self.statusQuoGoalChange)
        self.coalitionSelector.bind("<<CoalitionsChanged>>",self.coalitionChange)
            
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

    def statusQuoGoalChange(self,event=None):
        sq = self.statusQuoAndGoals.statusQuoSelector.current()
        goals = self.statusQuoAndGoals.getGoals()
        if len(goals)>0:
            self.sol = GoalSeeker(self.conflict,goals)
        else:
            self.sol = GoalSeeker(self.conflict)
        self.reachableTree.buildTree(sq,watchFor=[x[0] for x in goals])
        self.patternNarrator.updateNarration(goalInfo=self.reachableTree.goalInfo())
        
    def coalitionChange(self,event=None):
        sq = self.statusQuoAndGoals.statusQuoSelector.current()
        goals = self.statusQuoAndGoals.getGoals()
        if len(goals)>0:
            self.sol = GoalSeeker(self.conflict,goals)
        else:
            self.sol = GoalSeeker(self.conflict)
        self.reachableTree.buildTree(sq,watchFor=[x[0] for x in goals])
        self.patternNarrator.updateNarration(goalInfo=self.reachableTree.goalInfo())


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

    testFrame = StabilityFrame(cFrame,conf)
    if testFrame.hasRequiredData():
        testFrame.buildFrame()
    else:
        print("data missing")
        return
    testFrame.enter()



    root.mainloop()

if __name__ == '__main__':
    main()