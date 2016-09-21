# Copyright:   (c) Oskar Petersons 2013

"""Widgets for selecting a state using radio buttons for each option.

Loaded by the frame_02_infeasibles module.
"""

from tkinter import Tk, Canvas, N, S, E, W, VERTICAL, StringVar
from tkinter import ttk
from data_01_conflictModel import ConflictModel

tkNSEW = (N, S, E, W)


class RadiobuttonSeries(ttk.Labelframe):
    """State entry for a single decision maker."""

    def __init__(self, master=None, text=None, width=None, *args):
        """Initialize the widget."""
        ttk.Labelframe.__init__(self, master, text=text, width=width, *args)
        self.columnconfigure(0, weight=1)

        self.options = []
        self.stringVarList = []

        self.yLabel = ttk.Label(self, text='Y ', anchor="w")
        self.nLabel = ttk.Label(self, text='N ', anchor="w")
        self.oLabel = ttk.Label(self, text='Open', anchor="w")

        self.yLabel.grid(column=1, row=0)
        self.nLabel.grid(column=2, row=0)
        self.oLabel.grid(column=3, row=0)

        self.placeholder = False

        self.setOpts(self.options)

    def setOpts(self, options, *args):
        """Create Radiobutton inputs for each Option for the target DM."""
        if not options:
            self.placeholder = ttk.Label(self, text="This DM has no Options.")
            self.placeholder.grid(column=0, row=1, columnspan=4, sticky=tkNSEW)
            return None
        if self.placeholder:
            self.placeholder.grid_forget()
        self.options = options
        self.stringVarList = []

        for idx, opt in enumerate(self.options):
            self.stringVarList.append(StringVar(value='-'))
            yb = ttk.Radiobutton(self, variable=self.stringVarList[idx],
                                 value='Y', command=self.chgEvent)
            nb = ttk.Radiobutton(self, variable=self.stringVarList[idx],
                                 value='N', command=self.chgEvent)
            ob = ttk.Radiobutton(self, variable=self.stringVarList[idx],
                                 value='-', command=self.chgEvent)
            name = ttk.Label(self, text=opt.name)

            yb.grid(column=1, row=int(idx + 1), padx=(15, 10), pady=5)
            nb.grid(column=2, row=int(idx + 1), padx=(15, 10))
            ob.grid(column=3, row=int(idx + 1), padx=(15, 10))
            name.grid(column=0, row=int(idx + 1))

    def getStates(self, *args):
        """Get the input option selection in (idx,YN) format."""
        states = []
        for idx, bit in enumerate([x.get() for x in self.stringVarList]):
            if bit != '-':
                states.append((self.options[idx], bit))
        return states

    def chgEvent(self):
        """Trigger an event in the master frame if a change is made."""
        self.master.event_generate('<<RdBtnChg>>')


class RadiobuttonEntry(ttk.Frame):
    """State entry for the entire conflict.

    Uses a set of RadioButtonSeries elements.
    """

    def __init__(self, master, conflict):
        """Initialize the widget."""
        ttk.Frame.__init__(self, master)

        self.conflict = conflict

        self.rbeCanvas = Canvas(self)
        self.rdBtnFrame = ttk.Frame(self.rbeCanvas)
        self.scrollY = ttk.Scrollbar(self, orient=VERTICAL,
                                     command=self.rbeCanvas.yview)

        self.rbeCanvas.grid(column=0, row=0, columnspan=2, sticky=tkNSEW)
        self.scrollY.grid(column=2, row=0, sticky=tkNSEW)
        self.rbeCanvas.configure(yscrollcommand=self.scrollY.set)
        self.canvWindow = self.rbeCanvas.create_window(
            (0, 0), window=self.rdBtnFrame, anchor='nw')

        self.rowconfigure(0, weight=1)

        self.entryText = StringVar(value='')

        vcmd = self.register(self.onValidate)
        self.entryBx = ttk.Entry(self, textvariable=self.entryText,
                                 validate="key",
                                 validatecommand=(vcmd, '%S', '%P'))
        self.entryBx.grid(column=0, row=1, columnspan=2, sticky=tkNSEW)
        self.entryBx.bind('<Return>', self.generateAdd)

        self.warnText = StringVar(value='')

        self.addBtn = ttk.Button(self, text='Remove as Infeasible Condition',
                                 command=self.generateAdd)
        self.mutExBtn = ttk.Button(self,
                                   text='Remove as Mutually Exclusive Options',
                                   command=self.generateMutEx)
        self.warnLab = ttk.Label(self, textvariable=self.warnText)
        self.warnLab.grid(column=0, row=2, sticky=tkNSEW)
        self.addBtn.grid(column=0, row=3, columnspan=2, sticky=tkNSEW)
        self.mutExBtn.grid(column=0, row=4, columnspan=2, sticky=tkNSEW)

        self.reloadOpts()

    def resize(self, event=None):
        """Resize the scroll region of the main canvas element."""
        self.rbeCanvas.configure(scrollregion=self.rbeCanvas.bbox("all"))
        self.rbeCanvas["width"] = self.rbeCanvas.bbox("all")[2]

    def generateAdd(self, *args):
        """Prompt response to addition of an infeasible state."""
        self.event_generate('<<AddInfeas>>')

    def generateMutEx(self, *args):
        """Prompt response to addition of a mutually exclusive set."""
        self.event_generate('<<AddMutEx>>')

    def reloadOpts(self):
        """Reload all options for all DMs."""
        self.rbeCanvas.delete(self.canvWindow)
        self.rdBtnFrame.destroy()
        self.rdBtnFrame = ttk.Frame(self.rbeCanvas)
        self.canvWindow = self.rbeCanvas.create_window(
            (0, 0), window=self.rdBtnFrame, anchor='nw')
        self.rdBtnFrame.bind('<<RdBtnChg>>', self.rdBtnChgCmd)
        self.rdBtnFrame.bind("<Configure>", self.resize)

        self.rdBtnSrs = []
        self.stringVarList = []

        for x, dm in enumerate(self.conflict.decisionMakers):
            a = RadiobuttonSeries(self.rdBtnFrame, dm)
            self.rdBtnSrs.append(a)
            a.setOpts(dm.options)
            a.grid(column=0, row=int(x), sticky=tkNSEW)
            self.stringVarList += a.stringVarList

        self.rdBtnChgCmd()

    def setStates(self, dashOne):
        """Change the condition selected on the radio buttons."""
        if len(dashOne) != len(self.stringVarList):
            raise Exception('string length does not match number '
                            'of options: {}'.format(dashOne))
        for x, y in enumerate(dashOne):
            self.stringVarList[x].set(y)
        self.entryText.set(dashOne)

    def getStates(self):
        """Get the condition selected on the radio buttons."""
        states = []
        for srs in self.rdBtnSrs:
            states.extend(srs.getStates())
        return states

    def onValidate(self, chg, res):
        """Validate manually entered condition characters and length."""
        if chg in ['Y', 'N', 'y', 'n', '-']:
            if len(res) < len(self.stringVarList):
                self.warnText.set('Entry too short')
                return True
            if len(res) == len(self.stringVarList):
                self.setStates(res)
                self.warnText.set('')
                return True
        return False

    def rdBtnChgCmd(self, *args):
        """Set the entry box value to match the radiobuttons."""
        val = ''.join([x.get() for x in self.stringVarList])
        self.entryText.set(val)

# ######################


def main():
    """Run widget in test window."""
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    g1 = ConflictModel('Prisoners.gmcr')

    radFrame = RadiobuttonEntry(root, g1)
    radFrame.grid(column=0, row=0, sticky=(N, W))

    root.mainloop()

    print(radFrame.getStates())


if __name__ == '__main__':
    main()
