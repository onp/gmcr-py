# Copyright:   (c) Oskar Petersons 2013

"""Frame for editing misperceived states in the conflict.

Loaded by the a_Main_Window module, and implements all of its required
interfaces.
"""

from tkinter import *
from tkinter import ttk
from widgets_f02a_01_radioButtonEntry import RadiobuttonEntry
from widgets_f02a_02_infeasTreeview import TreeInfeas
from widgets_f02a_03_feasDisp import FeasDisp
from data_01_conflictModel import ConflictModel
import data_03_gmcrUtilities as gmcrUtil


class MisperceptionInpFrame(Frame):
    """Input frame for misperceived states."""

# ########################     INITIALIZATION  ################################
    def __init__(self, master, conflict, *args):
        """Initialize the Frame. Does not build widgets."""
        ttk.Frame.__init__(self, master, *args)

        self.infoFrame = ttk.Frame(master, relief='sunken', borderwidth='3')
        self.helpFrame = ttk.Frame(master, relief='sunken', borderwidth='3')

        # Connect to active conflict module
        self.conflict = conflict

        # Label used for button to select frame in the main program.
        self.buttonLabel = 'Infeasible States'
        # Image used on button to select frame, when frame is active.
        self.activeIcon = PhotoImage(file='icons/Infeasible_States_ON.gif')
        # Image used on button to select frame, when frame is inactive.
        self.inactiveIcon = PhotoImage(file='icons/Infeasible_States_OFF.gif')

        self.built = False

        self.lastBuildDMs = None
        self.lastBuildOptions = None
        self.lastBuildInfeasibles = None


# ############################     METHODS  ###################################

    def hasRequiredData(self):
        """Check that minimum data for input of misperceivedStates exists."""
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
        """Build all content for the Frame."""
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
        self.originalStatesText = StringVar(value='Original States: ' + 'init')
        self.removedStatesText = StringVar(value='States Removed: ' + 'init')
        self.feasStatesText = StringVar(value='States Remaining: ' + 'init')

        # Define variables that will display in the helpFrame
        self.helpText = StringVar(
            value="Enter misperceived states using the box at left. Removing "
            "as misperceived state will remove all states that match the "
            "pattern from the conflict. Removing as mutually exclusive will "
            "remove all states where ANY TWO OR MORE of the specified options "
            "occur together.")

        # Define frame-specific variables
        self.warnText = StringVar(value='')

        # infoFrame: frame and label definitions (with master 'self.infoFrame')
        self.originalStatesLabel = ttk.Label(self.infoFrame, textvariable=self.originalStatesText)
        self.removedStatesLabel = ttk.Label(self.infoFrame, textvariable=self.removedStatesText)
        self.feasStatesLabel = ttk.Label(self.infoFrame, textvariable=self.feasStatesText)

        # helpFrame: frame and label definitions (with master 'self.helpFrame')
        self.helpLabel = ttk.Label(self.helpFrame, textvariable=self.helpText, wraplength=150)

        # Define frame-specific input widgets (with 'self' as master)
        self.optsFrame = ttk.Frame(self)
        self.hSep = ttk.Separator(self, orient=VERTICAL)
        self.infeasFrame = ttk.Panedwindow(self, orient=HORIZONTAL)

        self.optsInp    = RadiobuttonEntry(self.optsFrame, self.conflict)
        self.infeasDisp = TreeInfeas(self.infeasFrame, self.conflict)
        self.feasList   = FeasDisp(self.infeasFrame, self.conflict)
        self.infeasFrame.add(self.infeasDisp)
        self.infeasFrame.add(self.feasList)

        # ########  preliminary gridding and option configuration

        # configuring the input frame
        self.grid(column=0, row=0, rowspan=5, sticky=(N,S,E,W))
        self.grid_remove()

        self.columnconfigure(2, weight=3)
        self.rowconfigure(0, weight=1)

        # configuring infoFrame & infoFrame widgets
        self.infoFrame.grid(column=2, row=0, sticky=(N,S,E,W), padx=3, pady=3)
        self.infoFrame.grid_remove()
        self.originalStatesLabel.grid(column=0, row=1, sticky=(N,S,E,W))
        self.removedStatesLabel.grid(column=0, row=2, sticky=(N,S,E,W))
        self.feasStatesLabel.grid(column=0, row=3, sticky=(N,S,E,W))

        # configuring helpFrame & helpFrame widgets
        self.helpFrame.grid(column=2, row=1, sticky=(N,S,E,W), padx=3, pady=3)
        self.helpFrame.grid_remove()
        self.helpLabel.grid(column=0, row=0, sticky=(N,S,E,W))

        # configuring frame-specific options
        self.optsFrame.columnconfigure(0, weight=1)
        self.optsFrame.rowconfigure(0, weight=1)
        self.optsFrame.grid(column=0, row=0, sticky=(N,S,E,W))

        self.infeasFrame.grid(column=2, row=0, sticky=(N,S,E,W))

        self.optsInp.grid(column=0, row=0, columnspan=2, sticky=(N,S,E,W))
        self.optsInp.bind('<<AddInfeas>>', self.addInfeas)
        self.optsInp.bind('<<AddMutEx>>', self.addMutEx)

        self.infeasDisp.bind('<<SelItem>>', self.selChg)
        self.infeasDisp.bind('<<ValueChange>>', self.refresh)

        self.hSep.grid(column=1, row=0, rowspan=10, sticky=(N,S,E,W))

        self.refresh()

        self.built = True

    def clearFrame(self):
        self.built = False
        for child in self.winfo_children():
            child.destroy()
        self.infoFrame.grid_forget()
        self.helpFrame.grid_forget()

    def refresh(self, *args):
        """Refresh information in the widgets. Triggered when data changes."""
        self.infeasDisp.refreshView()
        self.feasList.refreshList()
        numF = len(self.conflict.feasibles)
        numO = len(self.conflict.options)
        self.originalStatesText.set('Original States: %s' % (2**numO))
        self.feasStatesText.set('Feasible States: %s' % (numF))
        self.removedStatesText.set('States Removed: %s' % (2**numO - numF))

    def addInfeas(self, *args):
        """Remove an infeasible state from the conflict."""
        infeas = self.optsInp.getStates()
        self.conflict.infeasibles.append(infeas)
        self.conflict.recalculateFeasibleStates()
        self.refresh()

    def addMutEx(self, *args):
        """Remove a set of Mutually Exclusive States from the conflict."""
        mutEx = self.optsInp.getStates()
        mutEx = gmcrUtil.mutuallyExclusive(mutEx)
        for infeas in mutEx:
            self.conflict.infeasibles.append(list(infeas))
        self.refresh()

    def selChg(self, event):
        """Triggered when the selection changes in the treeview."""
        state = self.conflict.infeasibles[event.x].name
        self.optsInp.setStates(state)

    def enter(self):
        """Run when entering the Infeasible States screen."""
        if self.dataChanged():
            self.clearFrame()
        if not self.built:
            self.buildFrame()
        self.refresh()
        self.grid()
        self.infoFrame.grid()
        self.helpFrame.grid()
        if self.button:
            self.button['image'] = self.activeIcon
        self.optsInp.reloadOpts()

    def leave(self):
        """Run when leaving the Infeasible States screen."""
        self.grid_remove()
        self.infoFrame.grid_remove()
        self.helpFrame.grid_remove()
        if self.button:
            self.button['image'] = self.inactiveIcon


# ########
def main():
    """Run module in test window."""
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    cFrame = ttk.Frame(root)
    cFrame.columnconfigure(0, weight=1)
    cFrame.rowconfigure(1, weight=1)
    cFrame.grid(column=0, row=0, sticky=(N,S,E,W))

    hSep = ttk.Separator(cFrame, orient=VERTICAL)
    hSep.grid(column=1, row=0, rowspan=10, sticky=(N,S,E,W))

    g1 = ConflictModel('Prisoners.gmcr')

    testFrame = InfeasInpFrame(cFrame, g1)
    testFrame.enter()

    root.mainloop()


if __name__ == '__main__':
    main()
