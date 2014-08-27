# Copyright:   (c) Oskar Petersons 2013

"""Frame used to manually set decision maker's preferences.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel
from widgets_f05_01_PrefRank import PVecEditMaster
from widgets_f04_03_optionForm import OptionFormTable
import data_03_gmcrUtilities as gmcrUtil

class PreferenceVectorFrame(ttk.Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)
        
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')
        
        # Load up active game, if any
        self.game = game

        self.buttonLabel= 'Preference Ranking'     #Label used for button to select frame in the main program.
        self.activeIcon = PhotoImage(file='icons/Preference_Ranking_ON.gif')      #Image used on button to select frame, when frame is active.
        self.inactiveIcon = PhotoImage(file='icons/Preference_Ranking_OFF.gif')    #Image used on button to select frame, when frame is inactive.
        
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
        self.infoText = StringVar(value='')

        #Define variables that will display in the helpFrame
        self.helpText = StringVar(value="Use this screen to manually make small adjustments to "
                "preference vectors.  Any Changes made on this screen override preference "
                "prioritization inputs. Preference priorities will not be lost, in case you "
                "wish to revert to them later.")

        #Define frame-specific variables


        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.infoLabel  = ttk.Label(self.infoFrame,textvariable = self.infoText)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)

        #Define frame-specific input widgets (with 'self' or a child thereof as master)
        self.prefEditor = PVecEditMaster(self,self.game)
        self.stateTable = OptionFormTable(self,self.game)

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
        self.prefEditor.grid(row=0,column=0,sticky=(N,S,E,W))
        self.stateTable.grid(row=1,column=0,sticky=(N,S,E,W))
        self.columnconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)

        # bindings
        self.prefEditor.bind("<<PreferenceVectorChange>>",self.onPreferenceChange)
    
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
        self.prefEditor.refresh()
        self.stateTable.buildTable()
        
    def onPreferenceChange(self,event=None):
        self.stateTable.buildTable()



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