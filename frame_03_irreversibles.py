# Copyright:   (c) Oskar Petersons 2013

"""Frame allowing control over option reversibility.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import Tk, N, S, E, W, VERTICAL
from tkinter import ttk
from frame_00_frameTemplate import FrameTemplate
from data_01_conflictModel import ConflictModel
from widgets_f03_01_irreversibleToggles import IrreversibleSetter

tkNSEW = (N, S, E, W)


class IrrevInpFrame(FrameTemplate):
    """Frame allowing control over option reversibility."""

    # Label used for button to select frame in the main program.
    buttonLabel = 'Irreversible Moves'
    # Image used on button to select frame, when frame is active.
    activeIcon = 'icons/Irreversible_Moves_ON.gif'
    # Image used on button to select frame, when frame is inactive.
    inactiveIcon = 'icons/Irreversible_Moves_OFF.gif'
    # Help text to be displayed when screen is active.
    helpText = ("Specify the reversibility of moves by clicking the arrow "
                "until it correctly shows the direction(s) in which a move "
                "may be made.")

# ########################     INITIALIZATION  ################################
    def __init__(self, master, conflict, *args):
        """Initialize the Frame. Does not build widgets."""
        FrameTemplate.__init__(self, master, conflict, self.buttonLabel,
                               self.activeIcon, self.inactiveIcon,
                               self.helpText)

        self.lastBuildDMs = None

# ############################     METHODS  ###################################

    def hasRequiredData(self):
        """Check that minimum data required to render the frame exists."""
        if len(self.conflict.decisionMakers) < 1:
            return False
        if len(self.conflict.options) < 1:
            return False
        else:
            return True

    def dataChanged(self):
        """Check if data has changed since the last build of the Frame."""
        if self.lastBuildDMs != self.conflict.decisionMakers.export_rep():
            return True
        else:
            return False

    def buildFrame(self):
        """Contruct frame widgets and initialize data."""
        if self.built:
            return

        # Ensure all required parts of the conflict model are properly set-up.
        self.lastBuildDMs = self.conflict.decisionMakers.export_rep()

        # infoFrame: frame and label definitions (with master 'self.infoFrame')
        self.infoLabel = ttk.Label(self.infoFrame, text='')

        # helpFrame: frame and label definitions (with master 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame, textvariable=self.helpVar,
                                   wraplength=150)

        # Define frame-specific input widgets (with 'self' as master)
        self.irrevEntry = IrreversibleSetter(self, self.conflict)

        # ########  preliminary gridding and option configuration
        # configuring the input frame
        self.grid(column=0, row=0, rowspan=5, sticky=tkNSEW)
        self.grid_remove()
        self.columnconfigure(0, weight=1)

        # configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2, row=0, sticky=tkNSEW, padx=3, pady=3)
        self.infoFrame.grid_remove()
        self.infoLabel.grid(column=0, row=1, sticky=tkNSEW)

        # configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2, row=1, sticky=tkNSEW, padx=3, pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0, row=0, sticky=tkNSEW)

        # configuring frame-specific options
        self.irrevEntry.grid(column=0, row=0, sticky=tkNSEW)

        self.rowconfigure(0, weight=1)

        # bindings
        # None

        self.built = True

    def refreshWidgets(self, *args):
        """Refresh data in all active display widgets."""
        self.irrevEntry.refreshDisplay()

    def enter(self, *args):
        """Re-grid the screen into the master. Perform required updates."""
        if self.dataChanged():
            self.clearFrame()

        FrameTemplate.enter(self)


# #############################################################################
# ###############                   TESTING                         ###########
# #############################################################################

# Code in this section is only run when this module is run by itself. It serves
# as a test of module funcitonality.


def main():
    """Run screen in test window."""
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    cFrame = ttk.Frame(root)
    cFrame.columnconfigure(0, weight=1)
    cFrame.rowconfigure(1, weight=1)
    cFrame.grid(column=0, row=0, sticky=tkNSEW)

    hSep = ttk.Separator(cFrame, orient=VERTICAL)
    hSep.grid(column=1, row=0, rowspan=10, sticky=tkNSEW)

    testConflict = ConflictModel('Prisoners.gmcr')

    testFrame = IrrevInpFrame(cFrame, testConflict)
    testFrame.enter()

    root.mainloop()

if __name__ == '__main__':
    main()
