# Copyright:   (c) Oskar Petersons 2013

"""Frame for creating and editing decision makers and options.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import Tk, PhotoImage, StringVar, VERTICAL, N, S, E, W, END
from tkinter import ttk
from widgets_f01_01_dmOptElements import DMselector, DMeditor
from data_01_conflictModel import ConflictModel


class DMInpFrame(ttk.Frame):
    """Frame for input of DMs and options."""

# ########################     INITIALIZATION  ################################
    def __init__(self, master, conflict):
        ttk.Frame.__init__(self, master)

        self.infoFrame = ttk.Frame(master, relief='sunken', borderwidth='3')
        self.helpFrame = ttk.Frame(master, relief='sunken', borderwidth='3')

        # Connect to active conflict module
        self.conflict = conflict

        # Label used for button to select frame in the main program.
        self.buttonLabel = 'DMs & Options'
        # Image used on button to select frame, when frame is active.
        self.activeIcon = PhotoImage(file='icons/DMs_and_Options_ON.gif')
        # Image used on button to select frame, when frame is inactive.
        self.inactiveIcon = PhotoImage(file='icons/DMs_and_Options_OFF.gif')
        self.button = None

        self.built = False

# ############################     METHODS  ###################################
    def hasRequiredData(self):
        return True

    def buildFrame(self):
        if self.built:
            return
        # Define variables that will display in the infoFrame
        self.dmCount = StringVar(value='Number of Decision Makers: ' + 'init')
        self.optCount = StringVar(value='Number of Options: ' + 'init')
        self.stateCount = StringVar(value='Total States: ' + 'init')

        # Define variables that will display in the helpFrame
        self.helpText = StringVar(
            value="Click a decision maker in the left panel to view their "
            "associated options in the right panel.  Double clicking an entry "
            "or hitting 'Enter' with it selected allows you to edit it. "
            "Pressing 'Delete' with an entry selected will remove it.")

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
        self.grid(column=0, row=0, rowspan=5, sticky=(N,S,E,W))
        self.grid_remove()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        # configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2, row=0, sticky=(N,S,E,W), padx=3, pady=3)
        self.infoFrame.grid_remove()
        self.dmCountLabel.grid(column=0, row=1, sticky=(N,S,E,W))
        self.optCountLabel.grid(column=0, row=2, sticky=(N,S,E,W))
        self.stateCountLabel.grid(column=0, row=3, sticky=(N,S,E,W))

        # configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2, row=1, sticky=(N,S,E,W), padx=3, pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0, row=0, sticky=(N,S,E,W))

        # configuring frame-specific options
        self.dmSelector.grid(row=0, column=0, sticky=(N,S,E,W))
        ttk.Separator(self, orient=VERTICAL).grid(row=0, column=1, sticky=(N,S,E,W), padx=3)
        self.editor.grid(row=0, column=2, sticky=(N,S,E,W))

        # bindings
        self.dmSelector.bind('<<DMselected>>', self.dmChange)
        self.dmSelector.bind('<<EditDM>>', self.dmEdit)
        self.dmSelector.bind('<<dmOptChg>>', self.handleDMOptChange)
        self.editor.bind('<<dmOptChg>>', self.handleDMOptChange)
        self.editor.bind('<<dmNameChange>>', self.updateDMnames)

        self.built = True

    def clearFrame(self):
        if not self.built:
            return
        self.built = False
        for child in self.winfo_children():
            child.destroy()
        self.infoFrame.grid_forget()
        self.helpFrame.grid_forget()

    def refreshWidgets(self):
        self.dmSelector.refresh()
        self.dmSelector.reselect()
        self.updateTotals()

    def enter(self, *args):
        """Re-grid the screen into the master. Perform required updates."""
        if not self.built:
            self.buildFrame()
        self.refreshWidgets()
        self.grid()
        self.infoFrame.grid()
        self.helpFrame.grid()
        if self.button:
            self.button['image'] = self.activeIcon

    def leave(self, event=None):
        """Un-grid the screen. Perform exit update tasks."""
        self.grid_remove()
        self.infoFrame.grid_remove()
        self.helpFrame.grid_remove()
        if self.button:
            self.button['image'] = self.inactiveIcon

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
        self.conflict.useManualPreferenceRanking = False
        self.conflict.clearPreferences()
        self.event_generate('<<checkData>>')

        self.updateTotals()

    def updateDMnames(self, event=None):
        self.dmSelector.updateList()

    def updateTotals(self, event=None):
        numD = len(self.conflict.decisionMakers)
        numO = sum([len(dm.options) for dm in self.conflict.decisionMakers])
        self.dmCount.set('Number of Decision Makers: ' + str(numD))
        self.optCount.set('Number of Options: ' + str(numO))
        self.stateCount.set('Total States: ' + str(2**numO))

# ######################


def main():
    """Run screen in test window."""
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    cFrame = ttk.Frame(root)
    cFrame.columnconfigure(0, weight=1)
    cFrame.rowconfigure(1, weight=1)
    cFrame.grid(column=0, row=0, sticky=(N,S,E,W))

    hSep = ttk.Separator(cFrame, orient=VERTICAL)
    hSep.grid(column=1, row=0, rowspan=10, sticky=(N,S,E,W))

    g1 = ConflictModel('AmRv2.gmcr')

    testFrame = DMInpFrame(cFrame, g1)
    testFrame.enter()

    root.mainloop()

if __name__ == '__main__':
    main()
