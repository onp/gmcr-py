# Copyright:   (c) Oskar Petersons 2013

"""Frame used to create and display results of Inverse Approach solutions.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel
from widgets_f07_01_inverseContent import InverseContent



class InverseFrame(ttk.Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master,conflict,*args):
        ttk.Frame.__init__(self,master,*args)
        
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')

        self.conflict = conflict

        self.buttonLabel= 'Inverse GMCR'     #Label used for button to select frame in the main program.
        self.activeIcon = PhotoImage(file='icons/Inverse_GMCR_ON.gif')      #Image used on button to select frame, when frame is active.
        self.inactiveIcon = PhotoImage(file='icons/Inverse_GMCR_OFF.gif')    #Image used on button to select frame, when frame is inactive.
        
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
        self.helpText = StringVar(value="")

        #Define frame-specific variables


        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.infoLabel  = ttk.Label(self.infoFrame,textvariable = self.infoText)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)

        #Define frame-specific input widgets (with 'self' or a child thereof as master)
        self.invDisp = InverseContent(self,self.conflict)


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
        self.invDisp.grid(column=0,row=1,sticky=(N,S,E,W))

        # bindings
            #None
            
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
        self.invDisp.refreshDisplay()
        self.invDisp.refreshSolution()
        

    def leave(self,*args):
        """ Removes the main frame, infoFrame and helpFrame from the master,
        and performs any other update tasks required on exiting the frame."""
        self.grid_remove()
        del self.invDisp.sol
        self.infoFrame.grid_remove()
        self.helpFrame.grid_remove()
        if self.button:
            self.button['image'] = self.inactiveIcon




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

    testConflict = ConflictModel('pris.gmcr')

    testFrame = InverseFrame(cFrame,testConflict)
    testFrame.enter()



    root.mainloop()

if __name__ == '__main__':
    main()