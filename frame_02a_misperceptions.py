# Copyright:   (c) Oskar Petersons 2013

"""Frame for editing misperceived states in the conflict.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.

This frame is a repurposed "Infeasibles" frame and reuses most of the same
elements.
"""

from tkinter import Tk, StringVar, N, S, E, W, VERTICAL, HORIZONTAL
from tkinter import ttk
from frame_00_frameTemplate import FrameTemplate
from widgets_f02a_01_radioButtonEntry import RadiobuttonEntry
from widgets_f02a_02_infeasTreeview import TreeInfeas
from widgets_f02a_03_feasDisp import FeasDisp
from data_01_conflictModel import ConflictModel
import data_03_gmcrUtilities as gmcrUtil

tkNSEW = (N, S, E, W)


class MisperceptionFrame(FrameTemplate):
    """Frame for editing misperceived states in the conflict."""

    # Label used for button to select frame in the main program.
    buttonLabel = 'Misperceptions'
    # Image used on button to select frame, when frame is active.
    activeIcon = 'icons/Infeasible_States_ON.gif'
    # Image used on button to select frame, when frame is inactive.
    inactiveIcon = 'icons/Infeasible_States_OFF.gif'
    # Help text to be displayed when screen is active.
    helpText = ("Enter misperceived states using the box at left. Removing as "
                "misperceived state will remove all states that match the "
                "pattern from the conflict. Removing as mutually exclusive "
                "will remove all states where ANY TWO OR MORE of the specified"
                " options occur together.")

# ########################     INITIALIZATION  ################################
    def __init__(self, master, conflict, *args):
        """Initialize the Frame. Does not build widgets."""
        FrameTemplate.__init__(self, master, conflict, self.buttonLabel,
                               self.activeIcon, self.inactiveIcon,
                               self.helpText)

        self.lastBuildDMs = None
        self.lastBuildOptions = None
        self.lastBuildInfeasibles = None

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
        if self.lastBuildOptions != self.conflict.options.export_rep():
            return True
        if self.lastBuildInfeasibles != self.conflict.infeasibles.export_rep():
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

        self.lastBuildDMs = self.conflict.decisionMakers.export_rep()
        self.lastBuildOptions = self.conflict.options.export_rep()
        self.lastBuildInfeasibles = self.conflict.infeasibles.export_rep()

        # Define variables that will display in the infoFrame
        self.originalStatesText = StringVar(value='Original States: init')
        self.removedStatesText = StringVar(value='States Removed: init')
        self.feasStatesText = StringVar(value='States Remaining: init')

        # Define frame-specific variables
        self.warnText = StringVar(value='')
        self.activeDM = self.conflict.decisionMakers[0]

        # infoFrame: frame and label definitions (with master 'self.infoFrame')
        self.originalStatesLabel = ttk.Label(
            self.infoFrame, textvariable=self.originalStatesText)
        self.removedStatesLabel = ttk.Label(
            self.infoFrame, textvariable=self.removedStatesText)
        self.feasStatesLabel = ttk.Label(
            self.infoFrame, textvariable=self.feasStatesText)

        # helpFrame: frame and label definitions (with master 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame, textvariable=self.helpVar,
                                   wraplength=150)

        # Define frame-specific input widgets (with 'self' as master)
        self.optsFrame = ttk.Frame(self)
        self.hSep = ttk.Separator(self, orient=VERTICAL)
        self.infeasFrame = ttk.Panedwindow(self, orient=HORIZONTAL)

        self.optsInp = RadiobuttonEntry(self.optsFrame, self.conflict)
        self.infeasDisp = TreeInfeas(self.infeasFrame, self.conflict)
        self.feasList = FeasDisp(self.infeasFrame, self.conflict)
        self.infeasFrame.add(self.infeasDisp)
        self.infeasFrame.add(self.feasList)

        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0, row=0, rowspan=5, sticky=tkNSEW)
        self.grid_remove()

        self.columnconfigure(2, weight=3)
        self.rowconfigure(0, weight=1)

        # configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2, row=0, sticky=tkNSEW, padx=3, pady=3)
        self.infoFrame.grid_remove()
        self.originalStatesLabel.grid(column=0, row=1, sticky=tkNSEW)
        self.removedStatesLabel.grid(column=0, row=2, sticky=tkNSEW)
        self.feasStatesLabel.grid(column=0, row=3, sticky=tkNSEW)

        # configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2, row=1, sticky=tkNSEW, padx=3, pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0, row=0, sticky=tkNSEW)

        # configuring frame-specific options
        self.optsFrame.columnconfigure(0, weight=1)
        self.optsFrame.rowconfigure(0, weight=1)
        self.optsFrame.grid(column=0, row=0, sticky=tkNSEW)

        self.infeasFrame.grid(column=2, row=0, sticky=tkNSEW)

        self.optsInp.grid(column=0, row=0, columnspan=2, sticky=tkNSEW)
        self.optsInp.bind('<<addMisperceived>>', self.addMisperceived)
        self.optsInp.bind('<<AddMutEx>>', self.addMutEx)
        self.optsInp.bind('<<ChangeDM>>', self.changeDM)

        self.infeasDisp.bind('<<SelItem>>', self.selChg)
        self.infeasDisp.bind('<<ValueChange>>', self.refresh)

        self.hSep.grid(column=1, row=0, rowspan=10, sticky=tkNSEW)

        self.refresh()

        self.built = True

    def refresh(self, *args):
        """Refresh data in all active display widgets."""
        self.optsInp.activeDM = self.activeDM
        self.infeasDisp.activeDM = self.activeDM
        self.feasList.activeDM = self.activeDM
        self.activeDM.recalculatePerceived()
        self.infeasDisp.refresh()
        self.feasList.refresh()
        self.updateTotals()

    def updateTotals(self, event=None):
        """Update data shown in the infobox."""
        numO = len(self.conflict.options)
        numF = len(self.conflict.feasibles)
        self.originalStatesText.set('Original States: {}'.format(2**numO))
        self.feasStatesText.set('Feasible States: {}'.format(numF))
        self.removedStatesText.set('States Removed: {}'.format(2**numO - numF))

    def addMisperceived(self, *args):
        """Remove an infeasible state from the conflict."""
        misperceived = self.optsInp.getStates()
        self.activeDM.misperceptions.append(misperceived)
        self.refresh()

    def addMutEx(self, *args):
        """Remove a set of Mutually Exclusive States from the conflict."""
        mutEx = self.optsInp.getStates()
        mutEx = gmcrUtil.mutuallyExclusive(mutEx)
        for misperceived in mutEx:
            self.activeDM.misperceptions.append(list(misperceived))
        self.refresh()

    def selChg(self, event):
        """Triggered when the selection changes in the treeview."""
        state = self.activeDM.misperceptions[event.x].name
        self.optsInp.setStates(state)

    def enter(self):
        """Run when entering the Misperceived States screen."""
        if self.dataChanged():
            self.clearFrame()
        FrameTemplate.enter(self)
        self.optsInp.reloadOpts()

    def changeDM(self, *args):
        """Triggered when the focus DM is changed."""
        dmName = self.optsInp.activeDMname.get()
        self.activeDM = self.optsInp.dmLookup[dmName]
        self.refresh()

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

    g1 = ConflictModel()
    g1.load_from_file('Examples/SyriaIraq.gmcr')

    testFrame = MisperceptionFrame(cFrame, g1)
    testFrame.enter()

    root.mainloop()


if __name__ == '__main__':
    main()
