# Copyright:   (c) Oskar Petersons 2013

"""Frame used to manually set decision maker's preferences.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import Tk, StringVar, N, S, E, W, VERTICAL
from tkinter import ttk
from frame_00_frameTemplate import FrameTemplate
from data_01_conflictModel import ConflictModel
from widgets_f05_01_PrefRank import PRankEditMaster
from widgets_f04_03_optionForm import OptionFormTable

NSEW = (N, S, E, W)


class PreferenceRankingFrame(FrameTemplate):
    """Frame used to manually set decision maker's preferences."""

    # Label used for button to select frame in the main program.
    buttonLabel = 'Preference Ranking'
    # Image used on button to select frame, when frame is active.
    activeIcon = 'icons/Preference_Ranking_ON.gif'
    # Image used on button to select frame, when frame is inactive.
    inactiveIcon = 'icons/Preference_Ranking_OFF.gif'
    # Help text to be displayed when screen is active.
    helpText = ("Use this screen to manually make small adjustments to "
                "preference rankings.  Any Changes made on this screen "
                "override preference prioritization inputs. Preference "
                "priorities will not be lost, in case you wish to revert "
                "to them later.")

# ########################     INITIALIZATION  ################################
    def __init__(self, master, conflict, *args):
        """Initialize the Frame. Does not build widgets."""
        FrameTemplate.__init__(self, master, conflict, self.buttonLabel,
                               self.activeIcon, self.inactiveIcon,
                               self.helpText)

        self.lastBuildDMs = None
        self.lastBuildOptions = None
        self.lastBuildInfeasibles = None
        self.lastBuildRanking = None

# ############################     METHODS  ###################################

    def hasRequiredData(self):
        """Check that minimum data required to render the frame exists."""
        if len(self.conflict.decisionMakers) < 1:
            return False
        if len(self.conflict.options) < 1:
            return False
        if self.lastBuildRanking != self.conflict.useManualPreferenceRanking:
            return True
        if len(self.conflict.feasibles) < 1:
            self.conflict.recalculateFeasibleStates()
            if len(self.conflict.feasibles) < 1:
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

        for dm in self.conflict.decisionMakers:
            dm.calculatePerceived()
            dm.calculatePreferences()

        self.lastBuildDMs = self.conflict.decisionMakers.export_rep()
        self.lastBuildOptions = self.conflict.options.export_rep()
        self.lastBuildInfeasibles = self.conflict.infeasibles.export_rep()
        self.lastBuildRanking = self.conflict.useManualPreferenceRanking

        # Define variables that will display in the infoFrame
        self.infoText = StringVar(value='')

        # Define frame-specific variables

        # infoFrame: frame and label definitions (with master 'self.infoFrame')
        self.infoLabel = ttk.Label(self.infoFrame, textvariable=self.infoText)

        # helpFrame: frame and label definitions (with master 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame, textvariable=self.helpVar,
                                   wraplength=150)

        # Define frame-specific input widgets (with 'self' as master)
        self.prefEditor = PRankEditMaster(self, self.conflict)
        self.stateTable = OptionFormTable(self, self.conflict)

        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0, row=0, rowspan=5, sticky=NSEW)
        self.grid_remove()

        # configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2, row=0, sticky=NSEW, padx=3, pady=3)
        self.infoFrame.grid_remove()
        self.infoLabel.grid(column=0, row=1, sticky=NSEW)

        # configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2, row=1, sticky=NSEW, padx=3, pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0, row=0, sticky=NSEW)

        # configuring frame-specific options
        self.prefEditor.grid(row=0, column=0, sticky=NSEW)
        self.stateTable.grid(row=1, column=0, sticky=NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # bindings
        self.prefEditor.bind("<<PreferenceRankingChange>>",
                             self.onPreferenceChange)

        self.built = True

    def enter(self, *args):
        """Re-grid the screen into the master. Perform required updates."""
        if self.dataChanged():
            self.clearFrame()

        FrameTemplate.enter(self)

    def refresh(self, *args):
        """Refresh data in all active display widgets."""
        self.prefEditor.refresh()
        self.stateTable.buildTable()

    def onPreferenceChange(self, event=None):
        """Rebuild state table if preferences change."""
        self.stateTable.buildTable()


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
    cFrame.grid(column=0, row=0, sticky=NSEW)

    hSep = ttk.Separator(cFrame, orient=VERTICAL)
    hSep.grid(column=1, row=0, rowspan=10, sticky=NSEW)

    testConflict = ConflictModel('SyriaIraq.gmcr')

    testFrame = PreferenceRankingFrame(cFrame, testConflict)
    testFrame.enter()

    root.mainloop()

if __name__ == '__main__':
    main()
