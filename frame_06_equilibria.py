# Copyright:   (c) Oskar Petersons 2013

"""Frame for display of equilibria in the conflict.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.

Also includes functionality for exporting reachability data.
"""

from tkinter import (Tk, StringVar, N, S, E, W, VERTICAL, HORIZONTAL,
                     PanedWindow)
from tkinter import ttk
from frame_00_frameTemplate import FrameTemplate
from data_02_conflictSolvers import LogicalSolver
from widgets_f06_01_logResultDisp import (CoalitionSelector,
                                          OptionFormSolutionTable,
                                          Exporter,
                                          LogNarrator)

NSEW = (N, S, E, W)


class ResultFrame(FrameTemplate):
    """Frame for display of equilibria in the conflict."""

    # Label used for button to select frame in the main program.
    buttonLabel = 'Equilibria Results'
    # Image used on button to select frame, when frame is active.
    activeIcon = 'icons/Equilibria_Results_ON.gif'
    # Image used on button to select frame, when frame is inactive.
    inactiveIcon = 'icons/Equilibria_Results_OFF.gif'
    # Help text to be displayed when screen is active.
    helpText = ("The stability of each state in the conflict is shown in the "
                "table on the left, giving results under a number of different"
                " stability criterion. The display on the right allows the "
                "logic which defines the stability or instability of each "
                "option to be examined.")

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
        self.conflict.coalitions.validate()

        for dm in self.conflict.decisionMakers:
            dm.calculatePreferences()
            dm.calculatePerceived()

        self.lastBuildConflict = self.conflict.export_rep()

        # Define variables that will display in the infoFrame
        self.infoText = StringVar(value='')

        # Define frame-specific variables
        self.sol = LogicalSolver(self.conflict)
        self.sol.findEquilibria()

        # infoFrame: frame and label definitions (with master 'self.infoFrame')
        self.infoLabel = ttk.Label(self.infoFrame, textvariable=self.infoText)

        # helpFrame: frame and label definitions (with master 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame, textvariable=self.helpVar,
                                   wraplength=150)

        # Define frame-specific input widgets (with 'self' as master)
        self.paneMaster = PanedWindow(self, orient=HORIZONTAL, sashwidth=10,
                                      sashrelief="raised", sashpad=3,
                                      relief="sunken")

        self.pane1 = ttk.Frame(self.paneMaster)
        self.coalitionSelector = CoalitionSelector(self.pane1, self.conflict,
                                                   self)
        self.solutionTable = OptionFormSolutionTable(self.pane1, self.conflict,
                                                     self)
        self.exporter = Exporter(self.pane1, self.conflict, self)

        self.pane2 = ttk.Frame(self.paneMaster)
        self.narrator = LogNarrator(self.pane2, self.conflict, self)

        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0, row=0, rowspan=5, sticky=NSEW)
        self.grid_remove()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2, row=0, sticky=NSEW, padx=3, pady=3)
        self.infoFrame.grid_remove()
        self.infoLabel.grid(column=0, row=1, sticky=NSEW)

        # configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2, row=1, sticky=NSEW, padx=3, pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0, row=0, sticky=NSEW)

        # configuring frame-specific options
        self.paneMaster.grid(column=0, row=1, sticky=NSEW)
        self.paneMaster.add(self.pane1, width=600, stretch='always')
        self.pane1.rowconfigure(1, weight=1)
        self.pane1.columnconfigure(0, weight=1)
        self.coalitionSelector.grid(row=0, column=0, sticky=NSEW)
        self.solutionTable.grid(row=1, column=0, sticky=NSEW)
        self.exporter.grid(row=2, column=0, sticky=NSEW)

        self.paneMaster.add(self.pane2, width=250, stretch='always')
        self.pane2.rowconfigure(0, weight=1)
        self.pane2.columnconfigure(0, weight=1)
        self.narrator.grid(row=0, column=0, sticky=NSEW)

        # bindings
        self.coalitionSelector.bind("<<CoalitionsChanged>>",
                                    self.refresh)

        self.built = True

    def refresh(self, *args):
        """Refresh data in all active display widgets."""
        self.sol = LogicalSolver(self.conflict)
        self.sol.findEquilibria()
        self.coalitionSelector.refresh()
        self.solutionTable.refresh()
        self.narrator.refresh()


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
    cFrame.grid(column=0, row=0, sticky=NSEW)

    hSep = ttk.Separator(cFrame, orient=VERTICAL)
    hSep.grid(column=1, row=0, rowspan=10, sticky=NSEW)

    conf = ConflictModel()
    conf.load_from_file("save_files/Garrison.gmcr")

    testFrame = ResultFrame(cFrame, conf)
    if testFrame.hasRequiredData():
        testFrame.buildFrame()
    else:
        print("data missing")
        return
    testFrame.enter()

    root.mainloop()

if __name__ == '__main__':
    main()
