

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import *
from widgets_f03_01_irreversibleToggles import IrreversibleSetter


class IrrevInpFrame(ttk.Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master,game,*args):
        ttk.Frame.__init__(self,master,*args)

        self.game = game

        self.buttonLabel= 'Irreversible Moves'     #Label used for button to select frame in the main program.
        self.bigIcon=PhotoImage(file='icons/Irreversible.gif')         #Image used on button to select frame.

        #Define variables that will display in the infoFrame
        self.infoText = StringVar(value='information here reflects \nthe state of the module')

        #Define variables that will display in the helpFrame
        self.helpText = StringVar(value="Specify the reversibility of moves by clicking the arrow until it "
                "correctly shows the direction(s) in which the move may be made.")

        #Define frame-specific variables


        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')      #infoFrame master must be 'master'
        self.infoLabel  = ttk.Label(self.infoFrame,textvariable = self.infoText)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')      # helpFrame master must be 'master'
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)

        #Define frame-specific input widgets (with 'self' or a child therof as master)
        self.irrevEntry = IrreversibleSetter(self,self.game)


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
        self.irrevEntry.grid(column=0,row=0,sticky=(N,S,E,W))

        # bindings
            #None


# ############################     METHODS  #######################################


    def enter(self,*args):
        """ Re-grids the main frame, infoFrame and helpFrame into the master,
        and performs any other update tasks required on loading the frame."""
        self.grid()
        self.infoFrame.grid()
        self.helpFrame.grid()
        self.irrevEntry.refreshDisplay()

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
# as a test of module funcitonality.


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

    testGame = ConflictModel('Prisoners.gmcr')

    testFrame = IrrevInpFrame(cFrame,testGame)
    testFrame.enter()



    root.mainloop()

if __name__ == '__main__':
    main()