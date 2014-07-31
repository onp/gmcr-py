# Copyright:   (c) Oskar Petersons 2013

"""Frame for display of equilibria in the conflict.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.

Also includes functionality for exporting reachability data.
"""

from tkinter import *
from tkinter import ttk
from data_02_conflictSolvers import LogicalSolver
from widgets_f06_01_logResultDisp import *



class ResultFrame(ttk.Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master,conflict,*args):
        ttk.Frame.__init__(self,master,*args)
        
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')

        self.conflict = conflict

        self.buttonLabel= 'Equilibria Results'     #Label used for button to select frame in the main program.
        self.activeIcon = PhotoImage(file='icons/Equilibria_Results_ON.gif')      #Image used on button to select frame, when frame is active.
        self.inactiveIcon = PhotoImage(file='icons/Equilibria_Results_OFF.gif')    #Image used on button to select frame, when frame is inactive.
        
        self.built = False


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
            
    def buildFrame(self):
        if self.built:
            return
        #Define variables that will display in the infoFrame
        self.infoText = StringVar(value='')

        #Define variables that will display in the helpFrame
        self.helpText = StringVar(value=""
                "The stability of each state in the conflict is shown in the "
                "table on the left, giving results under a number of different "
                "stability criterion. The display on the right allows the logic "
                "which defines the stability or instability of each option to "
                "be examined.")

        #Define frame-specific variables
        self.sol = LogicalSolver(self.conflict)
        self.sol.findEquilibria()

        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.infoLabel  = ttk.Label(self.infoFrame,textvariable = self.infoText)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)

        #Define frame-specific input widgets (with 'self' or a child thereof as master)
        self.paneMaster = PanedWindow(self,orient=HORIZONTAL,sashwidth=10,sashrelief="raised",sashpad=3,relief="sunken")
        
        self.pane1 = ttk.Frame(self.paneMaster)
        self.coalitionSelector = CoalitionSelector(self.pane1,self.conflict,self)
        self.solutionTable = OptionFormSolutionTable(self.pane1,self.conflict,self)
        self.exporter = Exporter(self.pane1,self.conflict,self)
        
        self.pane2 = ttk.Frame(self.paneMaster)
        self.narrator = LogNarrator(self.pane2,self.conflict,self)


        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0,row=0,rowspan=5,sticky=(N,S,E,W))
        self.grid_remove()
        self.columnconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)

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
        self.paneMaster.add(self.pane1,width=600,stretch='always')
        self.pane1.rowconfigure(1,weight=1)
        self.pane1.columnconfigure(0,weight=1)
        self.coalitionSelector.grid(row=0,column=0,sticky=(N,S,E,W))
        self.solutionTable.grid(row=1,column=0,sticky=(N,S,E,W))
        self.exporter.grid(row=2,column=0,sticky=(N,S,E,W))
        
        self.paneMaster.add(self.pane2,width=250,stretch='always')
        self.pane2.rowconfigure(0,weight=1)
        self.pane2.columnconfigure(0,weight=1)
        self.narrator.grid(row=0,column=0,sticky=(N,S,E,W))


        # bindings
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
        self.grid()
        self.infoFrame.grid()
        self.helpFrame.grid()
        self.sol = LogicalSolver(self.conflict)
        self.sol.findEquilibria()
        self.coalitionSelector.refresh()
        self.solutionTable.refresh()
        self.narrator.refresh()
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

    def coalitionChange(self,event=None):
        self.sol = LogicalSolver(self.conflict)
        self.sol.findEquilibria()
        self.coalitionSelector.refresh()
        self.solutionTable.refresh()
        self.narrator.refresh()





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

    testFrame = ResultFrame(cFrame,conf)
    if testFrame.hasRequiredData():
        testFrame.buildFrame()
    else:
        print("data missing")
        return
    testFrame.enter()



    root.mainloop()

if __name__ == '__main__':
    main()