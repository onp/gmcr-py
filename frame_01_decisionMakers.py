# Copyright:   (c) Oskar Petersons 2013

"""Frame for creating and editing decision makers and options.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import Tk, StringVar, VERTICAL, N, S, E, W, END
from tkinter import ttk
from frame_00_frameTemplate import FrameTemplate
from widgets_f01_01_dmOptElements import DMselector, DMeditor
from data_01_conflictModel import ConflictModel

tkNSEW = (N, S, E, W)


class DMInpFrame(FrameTemplate):
    """Frame for input of DMs and options."""

    # Label used for button to select frame in the main program.
    buttonLabel = 'DMs & Options'
    # Image used on button to select frame, when frame is active.
    activeIcon = 'icons/DMs_and_Options_ON.gif'
    # Image used on button to select frame, when frame is inactive.
    inactiveIcon = 'icons/DMs_and_Options_OFF.gif'
    # Help text to be displayed when screen is active.
    helpText = """Click a decision maker in the left panel to view their \
    associated options in the right panel.  Double clicking an entry or \
    hitting 'Enter' with it selected allows you to edit it. Pressing 'Delete' \
    with an entry selected will remove it."""

# ########################     INITIALIZATION  ################################
    def __init__(self, master, conflict):
        """Initialize DMinput Frame."""
        FrameTemplate.__init__(self, master, conflict, self.buttonLabel,
                               self.activeIcon, self.inactiveIcon)

# ############################     METHODS  ###################################

    def buildFrame(self):
        """Contruct frame widgets and initialize data."""
        if self.built:
            return
        # Define variables that will display in the infoFrame
        self.dmCount = StringVar(value='Number of Decision Makers: ' + 'init')
        self.optCount = StringVar(value='Number of Options: ' + 'init')
        self.stateCount = StringVar(value='Total States: ' + 'init')

        # Define frame-specific variables

        # infoFrame: frame and label definitions (with master 'self.infoFrame')
        self.dmCountLabel = ttk.Label(self.infoFrame,
                                      textvariable=self.dmCount)
        self.optCountLabel = ttk.Label(self.infoFrame,
                                       textvariable=self.optCount)
        self.stateCountLabel = ttk.Label(self.infoFrame,
                                         textvariable=self.stateCount)

        # helpFrame: frame and label definitions (with master 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame, textvariable=self.helpText,
                                   wraplength=150)

        # Define frame-specific input widgets
        # (with master 'self' or a child thereof)
        self.dmSelector = DMselector(self, self.conflict)
        self.editor = DMeditor(self, self.conflict)

        # ########  preliminary griding and option configuration

        # configuring the input frame
        self.grid(column=0, row=0, rowspan=5, sticky=tkNSEW)
        self.grid_remove()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        # configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2, row=0, sticky=tkNSEW, padx=3, pady=3)
        self.infoFrame.grid_remove()
        self.dmCountLabel.grid(column=0, row=1, sticky=tkNSEW)
        self.optCountLabel.grid(column=0, row=2, sticky=tkNSEW)
        self.stateCountLabel.grid(column=0, row=3, sticky=tkNSEW)

        # configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2, row=1, sticky=tkNSEW, padx=3, pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0, row=0, sticky=tkNSEW)

        # configuring frame-specific options
        self.dmSelector.grid(row=0, column=0, sticky=tkNSEW)
        ttk.Separator(self, orient=VERTICAL).grid(row=0, column=1,
                                                  sticky=tkNSEW, padx=3)
        self.editor.grid(row=0, column=2, sticky=tkNSEW)

        # bindings
        self.dmSelector.bind('<<DMselected>>', self.dmChange)
        self.dmSelector.bind('<<EditDM>>', self.dmEdit)
        self.dmSelector.bind('<<dmOptChg>>', self.handleDMOptChange)
        self.editor.bind('<<dmOptChg>>', self.handleDMOptChange)
        self.editor.bind('<<dmNameChange>>', self.updateDMnames)

        self.built = True

    def refreshWidgets(self):
        """Refresh data in all active display widgets."""
        self.dmSelector.refresh()
        self.dmSelector.reselect()
        self.updateTotals()

    def dmChange(self, event=None):
        """Change the selected decision maker."""
        self.editor.loadDM(self.dmSelector.selectedDM)

    def dmEdit(self, event=None):
        """Push focus to the DM's name editing box. Create new DM if needed."""
        if self.dmSelector.selectedDM is None:
            self.conflict.decisionMakers.append("New Decision Maker")
            self.dmSelector.refresh()
            self.dmSelector.reselect()
        self.dmSelector.dmListDisp.selection_set(self.dmSelector.selIdx)
        self.editor.dmNameEditor.focus()
        self.editor.dmNameEditor.select_range(0, END)

    def handleDMOptChange(self, event=None):
        """Update data when a DM or option is changed."""
        self.conflict.useManualPreferenceRanking = False
        self.conflict.clearPreferences()
        self.event_generate('<<checkData>>')

        self.updateTotals()

    def updateDMnames(self, event=None):
        """Update screen when a DM name is changed."""
        self.dmSelector.updateList()

    def updateTotals(self, event=None):
        """Update data shown in the infobox."""
        numD = len(self.conflict.decisionMakers)
        numO = sum([len(dm.options) for dm in self.conflict.decisionMakers])
        self.dmCount.set('Number of Decision Makers: {}'.format(numD))
        self.optCount.set('Number of Options: {}'.format(numO))
        self.stateCount.set('Total States: {}'.format(2**numO))

# ######################


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

    g1 = ConflictModel('AmRv2.gmcr')

    testFrame = DMInpFrame(cFrame, g1)
    testFrame.enter()

    root.mainloop()

if __name__ == '__main__':
    main()
