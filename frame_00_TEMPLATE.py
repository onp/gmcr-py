# Template for input frames.  Shows the methods and attributes neccesary for
#  interfacing with the main program

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel


class InpFrameTemplate(ttk.Frame):
# ########################     INITIALIZATION  ####################################
    def __init__(self,master=None,activeGame=None,*args):
        ttk.Frame.__init__(self,master,*args)

        self.buttonLabel= 'Template InputFrame'     #Label used for button to select frame in the main program.
        self.bigIcon=PhotoImage(file='bigIcon.gif')         #Image used on button to select frame.

        #Define variables that will display in the infoFrame
        self.infoText = StringVar(value='information here reflects \nthe state of the module')

        #Define variables that will display in the helpFrame
        self.helpText = StringVar(value='lots and lots of words about relevant stuff and instructions and so on and on and on and on and on.')

        #Define frame-specific variables
        self.placeHolderText = StringVar(value = 'this is a place for the input interface to go')


        # infoFrame : frame and label definitions   (with master of 'self.infoFrame')
        self.infoFrame = ttk.Frame(master,relief='sunken',borderwidth='3')      #infoFrame master must be 'master'
        self.infoLabel  = ttk.Label(self.infoFrame,textvariable = self.infoText)

        # helpFrame : frame and label definitions (with master of 'self.helpFrame')
        self.helpFrame = ttk.Frame(master,relief='sunken',borderwidth='3')      # helpFrame master must be 'master'
        self.helpLabel = ttk.Label(self.helpFrame,textvariable=self.helpText, wraplength=150)

        #Define frame-specific input widgets (with 'self' or a child therof as master)
        self.placeHolderLabel = ttk.Label(self,textvariable = self.placeHolderText,anchor = 'center')

        # Load up active game, if any
        if activeGame:
            self.setGame(activeGame)

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
        self.placeHolderLabel.grid(column=0,row=0,sticky=(N,S,E,W))

        # bindings
            #None


# ############################     METHODS  #######################################

    def setGame(self,newGame):
        """ Changes the Game Object attached to the frame, updates the contents
        of the Frame as required."""
        self.activeGame = newGame

    def enter(self,*args):
        """ Re-grids the main frame, infoFrame and helpFrame into the master,
        and performs any other update tasks required on loading the frame."""
        self.setGame(self.activeGame)
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

    testGame = ConflictModel('AmRv2.gmcr')

    testFrame = InpFrameTemplate(cFrame,testGame)
    testFrame.enter()



    root.mainloop()

if __name__ == '__main__':
    main()