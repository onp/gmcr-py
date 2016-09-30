# Copyright:   (c) Oskar Petersons 2013

"""Frame used to create and display results of Inverse Approach solutions.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import Tk, N, S, E, W, VERTICAL
from tkinter import ttk
from frame_00_frameTemplate import FrameTemplate
from data_01_conflictModel import ConflictModel
from widgets_f07_01_inverseContent import InverseContent

tkNSEW = (N, S, E, W)


class InverseFrame(FrameTemplate):
    """Calculate and display results of Inverse Approach solutions."""

    # Label used for button to select frame in the main program.
    buttonLabel = 'Inverse GMCR'
    # Image used on button to select frame, when frame is active.
    activeIcon = 'icons/Inverse_GMCR_ON.gif'
    # Image used on button to select frame, when frame is inactive.
    inactiveIcon = 'icons/Inverse_GMCR_OFF.gif'
    # Help text to be displayed when screen is active.
    helpText = ("")

# ########################     INITIALIZATION  ################################
    def __init__(self, master, conflict, *args):
        """Initialize the Frame. Does not build widgets."""
        FrameTemplate.__init__(self, master, conflict, self.buttonLabel,
                               self.activeIcon, self.inactiveIcon,
                               self.helpText)

        self.lastBuildConflict = None

# ############################     METHODS  ###################################

    def hasRequiredData(self):
        """Check that minimum data required to render the frame exists."""
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
        """Check if data has changed since the last build of the Frame."""
        if self.lastBuildConflict != self.conflict.export_rep():
            return True
        else:
            return False

    def buildFrame(self):
        """Contruct frame widgets and initialize data."""
        if self.built:
            return

        # Ensure all required parts of the conflict model are properly set-up.
        self.conflict.reorderOptionsByDM()
        self.conflict.options.set_indexes()
        self.conflict.infeasibles.validate()
        self.conflict.recalculateFeasibleStates()

        for dm in self.conflict.decisionMakers:
            dm.calculatePreferences()
            dm.calculatePerceived()

        self.lastBuildConflict = self.conflict.export_rep()

        # Define frame-specific variables

        # infoFrame: frame and label definitions (with master 'self.infoFrame')
        self.infoLabel = ttk.Label(self.infoFrame, text="")

        # helpFrame: frame and label definitions (with master 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame, textvariable=self.helpVar,
                                   wraplength=150)

        # Define frame-specific input widgets (with 'self' as master)
        self.invDisp = InverseContent(self, self.conflict)

        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0, row=0, rowspan=5, sticky=tkNSEW)
        self.grid_remove()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2, row=0, sticky=tkNSEW, padx=3, pady=3)
        self.infoFrame.grid_remove()
        self.infoLabel.grid(column=0, row=1, sticky=tkNSEW)

        # configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2, row=1, sticky=tkNSEW, padx=3, pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0, row=0, sticky=tkNSEW)

        # configuring frame-specific options
        self.invDisp.grid(column=0, row=1, sticky=tkNSEW)

        # bindings

        self.built = True

    def resfresh(self):
        """Refresh data in all active display widgets."""
        self.invDisp.refreshDisplay()
        self.invDisp.refreshSolution()

    def leave(self, *args):
        """Un-grid the screen. Perform exit clean-up tasks."""
        FrameTemplate.leave(self)
        del self.invDisp.sol


# #############################################################################
# ###############                   TESTING                         ###########
# #############################################################################

# Code in this section is only run when this module is run by itself. It serves
# as a test of module functionality.


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

    testConflict = ConflictModel('pris.gmcr')

    testFrame = InverseFrame(cFrame, testConflict)
    testFrame.enter()

    root.mainloop()

if __name__ == '__main__':
    main()
