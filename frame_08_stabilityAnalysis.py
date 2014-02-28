# Copyright:   (c) Oskar Petersons 2013

"""Frame used to for Stability Analysis.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import *
from tkinter import ttk
from widgets_f08_01_stabilityAnalysis import *



class StabilityFrame(ttk.Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master,conflict,*args):
        ttk.Frame.__init__(self,master,*args)
        
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')

        self.conflict = conflict

        self.buttonLabel= 'Stability'     #Label used for button to select frame in the main program.
        self.bigIcon=PhotoImage(file='icons/Equilibria.gif')         #Image used on button to select frame.
        
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
        self.infoText = StringVar(value='information here reflects \nthe state of the module')

        #Define variables that will display in the helpFrame
        self.helpText = StringVar(value="help box for the stability analysis screen.")

        #Define frame-specific variables


        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.infoLabel  = ttk.Label(self.infoFrame,textvariable = self.infoText)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)

        #Define frame-specific input widgets (with 'self' or a child thereof as master)
        self.goalstuff = StatusQuoAndGoals(self,self.conflict)

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
        self.goalstuff.grid(row=0,column=0,sticky=(N,S,E,W))

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
        self.grid()
        self.infoFrame.grid()
        self.helpFrame.grid()

    def leave(self,*args):
        """ Removes the main frame, infoFrame and helpFrame from the master,
        and performs any other update tasks required on exiting the frame."""
        self.grid_remove()
        self.infoFrame.grid_remove()
        self.helpFrame.grid_remove()




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