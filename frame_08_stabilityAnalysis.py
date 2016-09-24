# Copyright:   (c) Oskar Petersons 2013

"""Frame used to for Stability Analysis.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import Tk, N, S, E, W, PanedWindow, HORIZONTAL, VERTICAL
from tkinter import ttk
from frame_00_frameTemplate import FrameTemplate
from data_02_conflictSolvers import GoalSeeker
from widgets_f06_01_logResultDisp import CoalitionSelector
from widgets_f04_03_optionForm import OptionFormTable
from widgets_f08_01_stabilityAnalysis import (StatusQuoAndGoals,
                                              ReachableTreeViewer,
                                              PatternNarrator)

tkNSEW = (N, S, E, W)


class StabilityFrame(FrameTemplate):
    """Frame used to for Stability Analysis."""

    # Label used for button to select frame in the main program.
    buttonLabel = 'Post Analysis'
    # Image used on button to select frame, when frame is active.
    activeIcon = 'icons/Post_Analysis_ON.gif'
    # Image used on button to select frame, when frame is inactive.
    inactiveIcon = 'icons/Post_Analysis_OFF.gif'
    # Help text to be displayed when screen is active.
    helpText = ("Selecting coalitions, status quo and goals at the top left"
                "will generate a reachability tree below the status quo, and "
                "detail the patterns that preferences must match for the goal "
                "state to be reached.")

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
            dm.recalculatePerceived()

        self.lastBuildConflict = self.conflict.export_rep()

        # Define frame-specific variables
        self.sol = GoalSeeker(self.conflict)

        # infoFrame: frame and label definitions (with master 'self.infoFrame')
        self.infoLabel = ttk.Label(self.infoFrame, text="")

        # helpFrame: frame and label definitions (with master 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame, textvariable=self.helpVar,
                                   wraplength=150)

        # Define frame-specific input widgets (with 'self' as master)
        self.paneMaster = PanedWindow(self, orient=HORIZONTAL, sashwidth=10,
                                      sashrelief="raised", sashpad=3,
                                      relief="sunken")

        self.paneLeft = PanedWindow(self.paneMaster, orient=VERTICAL,
                                    sashwidth=10, sashrelief="raised",
                                    sashpad=3, relief="sunken")

        self.paneLeftTop = ttk.Frame(self.paneLeft)
        self.coalitionSelector = CoalitionSelector(self.paneLeftTop,
                                                   self.conflict, self)
        self.statusQuoAndGoals = StatusQuoAndGoals(self.paneLeftTop,
                                                   self.conflict)
        self.reachableTree = ReachableTreeViewer(self.paneLeftTop,
                                                 self.conflict, self)

        self.paneLeftBottom = ttk.Frame(self.paneLeft)
        self.optionFormTable = OptionFormTable(self.paneLeftBottom,
                                               self.conflict)

        self.paneRight = ttk.Frame(self.paneMaster)
        self.patternNarrator = PatternNarrator(self.paneRight, self.conflict,
                                               self)

        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0, row=0, rowspan=5, sticky=tkNSEW)
        self.grid_remove()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2, row=0, sticky=tkNSEW, padx=3, pady=3)
        self.infoFrame.grid_remove()
        self.infoLabel.grid(column=0, row=1, sticky=tkNSEW)

        # configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2, row=1, sticky=tkNSEW, padx=3, pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0, row=0, sticky=tkNSEW)

        # configuring frame-specific options
        self.paneMaster.grid(row=0, column=0, sticky=tkNSEW)

        self.paneMaster.add(self.paneLeft)

        self.paneLeft.add(self.paneLeftTop)
        self.paneLeftTop.columnconfigure(1, weight=1)
        self.paneLeftTop.rowconfigure(2, weight=1)
        self.coalitionSelector.grid(row=0, column=0, sticky=tkNSEW)
        ttk.Separator(self, orient=HORIZONTAL).grid(row=1, column=0,
                                                    sticky=tkNSEW, pady=3)
        self.statusQuoAndGoals.grid(row=2, column=0, sticky=tkNSEW)
        self.reachableTree.grid(row=0, column=1, rowspan=3, sticky=tkNSEW)

        self.paneLeft.add(self.paneLeftBottom)
        self.paneLeftBottom.rowconfigure(0, weight=1)
        self.paneLeftBottom.columnconfigure(0, weight=1)
        self.optionFormTable.grid(row=0, column=0, sticky=tkNSEW)

        self.paneMaster.add(self.paneRight)
        self.paneRight.rowconfigure(0, weight=1)
        self.paneRight.columnconfigure(0, weight=1)
        self.patternNarrator.grid(row=0, column=0, sticky=tkNSEW)

        # bindings
        self.statusQuoAndGoals.bind("<<StatusQuoChanged>>",
                                    self.refresh)
        self.statusQuoAndGoals.bind("<<GoalChanged>>",
                                    self.refresh)
        self.coalitionSelector.bind("<<CoalitionsChanged>>",
                                    self.refresh)

        self.built = True

    def refresh(self):
        """Refresh data in all active display widgets."""
        sq = self.statusQuoAndGoals.statusQuoSelector.current()
        goals = self.statusQuoAndGoals.getGoals()
        if len(goals) > 0:
            self.sol = GoalSeeker(self.conflict, goals)
        else:
            self.sol = GoalSeeker(self.conflict)
        self.reachableTree.buildTree(sq, watchFor=[x[0] for x in goals])
        self.patternNarrator.updateNarration(
            goalInfo=self.reachableTree.goalInfo())


# #############################################################################
# ###############                   TESTING                         ###########
# #############################################################################

# Code in this section is only run when this module is run by itself. It serves
# as a test of module functionality.


def main():
    """Run screen in test window."""
    from data_01_conflictModel import ConflictModel

    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    cFrame = ttk.Frame(root)
    cFrame.columnconfigure(0, weight=1)
    cFrame.rowconfigure(1, weight=1)
    cFrame.grid(column=0, row=0, sticky=tkNSEW)

    hSep = ttk.Separator(cFrame, orient=VERTICAL)
    hSep.grid(column=1, row=0, rowspan=10, sticky=tkNSEW)

    conf = ConflictModel()
    conf.load_from_file("save_files/Garrison.gmcr")

    testFrame = StabilityFrame(cFrame, conf)
    if testFrame.hasRequiredData():
        testFrame.buildFrame()
    else:
        print("data missing")
        return
    testFrame.enter()

    root.mainloop()

if __name__ == '__main__':
    main()
