# Copyright:   (c) Oskar Petersons 2013

"""Widget for displaying all of the perceived states for a DM.

Loaded by the frame_02a_misperceptions module.
Copied from a very similar widget used on the infeasibles screen.
"""

from tkinter import Tk, N, S, E, W, VERTICAL, StringVar, Listbox
from tkinter import ttk
from data_01_conflictModel import ConflictModel

tkNSEW = (N, S, E, W)


class FeasDisp(ttk.Frame):
    """Widget for displaying all of the feasible states in the conflict."""

    def __init__(self, master=None, conflict=None, *args):
        """Initialize the widget."""
        ttk.Frame.__init__(self, master, padding=5)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.conflict = conflict

        self.dispFormat = StringVar(value='pattern')
        self.dispList = StringVar()
        self.feasList = []

        self.fmts = {'Pattern': 'YN-', 'List (YN)': 'YN',
                     'List (ordered and [decimal])': 'ord_dec'}
        cBoxOpts = ('Pattern', 'List (YN)', 'List (ordered and [decimal])')
        self.feasText = ttk.Label(self, text='Perceived States')
        self.feasText.grid(row=0, column=0, columnspan=3)
        self.cBox = ttk.Combobox(self, textvariable=self.dispFormat,
                                 values=cBoxOpts, state='readonly')
        self.cBoxLb = ttk.Label(self, text='Format:')
        self.feasLBx = Listbox(self, listvariable=self.dispList)
        self.scrl = ttk.Scrollbar(self, orient=VERTICAL,
                                  command=self.feasLBx.yview)

        # ###########
        self.cBoxLb.grid(column=0, row=1, sticky=tkNSEW, pady=3)
        self.cBox.grid(column=1, row=1, columnspan=2, sticky=tkNSEW, pady=3)
        self.feasLBx.grid(column=0, row=2, columnspan=2, sticky=tkNSEW)
        self.scrl.grid(column=2, row=2, sticky=tkNSEW)

        self.cBox.bind('<<ComboboxSelected>>', self.fmtSel)
        self.feasLBx.configure(yscrollcommand=self.scrl.set)

        self.dispFormat.set('Pattern')
        self.fmtSel()

    def fmtSel(self, *args):
        """Action on selection of a new format."""
        self.refresh()

    def setFeas(self, feasList):
        """Change the list of feasible states to be displayed."""
        self.feasList = feasList
        self.refresh()

    def refresh(self):
        """Update the list of perceived states displayed and the format."""
        self.activeDM.recalculatePerceived()
        fmt = self.fmts[self.dispFormat.get()]
        if fmt == "YN-":
            perc = self.activeDM.perceived.dash
        if fmt == "YN":
            perc = self.activeDM.perceived.yn
        if fmt == "ord_dec":
            perc = self.activeDM.perceived.ordDec
        self.dispList.set(tuple(perc))


def main():
    """Run widget in test window."""
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    g1 = ConflictModel('Prisoners.gmcr')

    FeasView = FeasDisp(root, g1)
    FeasView.grid(column=0, row=0, sticky=tkNSEW)

    root.mainloop()

if __name__ == '__main__':
    main()
