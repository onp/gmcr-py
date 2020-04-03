# Copyright:   (c) Oskar Petersons 2013

"""Widgets displaying the results of Inverse Approach analysis.

Loaded by the frame_07_inverseApproach module.
"""

from tkinter import (Tk, N, S, E, W, VERTICAL, HORIZONTAL, StringVar,
                     Text, Canvas)
from tkinter import ttk
from data_01_conflictModel import ConflictModel
from data_02_conflictSolvers import InverseSolver
import numpy as np
from math import factorial

NSEW = (N, S, E, W)


class VaryRangeSelector(ttk.Frame):
    def __init__(self, master, conflict, *args):
        ttk.Frame.__init__(self, master, *args)

        self.vrsCanvas = Canvas(self)
        self.vrsFrame = ttk.Frame(self.vrsCanvas)
        self.scrollY = ttk.Scrollbar(self, orient=VERTICAL,
                                     command=self.vrsCanvas.yview)

        self.vrsCanvas.grid(column=0, row=0, columnspan=1, sticky=NSEW)
        self.scrollY.grid(column=2, row=0, sticky=NSEW)
        self.vrsCanvas.configure(yscrollcommand=self.scrollY.set)
        self.canvWindow = self.vrsCanvas.create_window((0, 0),
                                                       window=self.vrsFrame,
                                                       anchor='nw')
        self.vrsFrame.bind("<Configure>", self.resize)
        self.rowconfigure(0, weight=1)

        self.conflict = conflict
        self.vary = [[0, 0] for dm in self.conflict.decisionMakers]

        self.varyVar = []
        self.varyDispVar = []

        for dmIdx, dm in enumerate(self.conflict.decisionMakers):
            dmFrame = ttk.Labelframe(self.vrsFrame, text=dm.name)
            dmFrame.grid(column=0, row=dmIdx)

            dispVar = StringVar(value='No range selected. Using original '
                                'ranking.')

            t = 'Original ranking: ' + str(dm.preferenceRanking)

            ttk.Label(dmFrame, text=t, wraplength=500).grid(column=0, row=1,
                                                            columnspan=4,
                                                            sticky=NSEW)

            ttk.Label(dmFrame, textvariable=dispVar,
                      wraplength=500).grid(column=0, row=2, columnspan=4,
                                           sticky=NSEW)

            ttk.Label(dmFrame, text='Vary from:').grid(column=0, row=0)
            startSel = ttk.Combobox(dmFrame, state='readonly')
            startSel['values'] = tuple(dm.preferenceRanking)
            startSel.current(0)
            startSel.grid(column=1, row=0)
            startSel.bind('<<ComboboxSelected>>', self.chgVary)

            ttk.Label(dmFrame, text='  to:').grid(column=2, row=0)
            endSel = ttk.Combobox(dmFrame, state='readonly')
            endSel['values'] = tuple(dm.preferenceRanking)
            endSel.current(0)
            endSel.grid(column=3, row=0)
            endSel.bind('<<ComboboxSelected>>', self.chgVary)

            self.varyVar.append([startSel, endSel])
            self.varyDispVar.append(dispVar)

    def resize(self, event=None):
        """Adjust the canvas widget if the window is resized."""
        self.vrsCanvas.configure(scrollregion=self.vrsCanvas.bbox("all"))
        self.vrsCanvas["width"] = self.vrsCanvas.bbox("all")[2]

    def chgVary(self, *args):
        self.vary = [[0, 0] for dm in self.conflict.decisionMakers]
        for dmIdx, rangeForDM in enumerate(self.varyVar):
            dm = self.conflict.decisionMakers[dmIdx]
            v1 = rangeForDM[0].current()
            v2 = rangeForDM[1].current() + 1
            if (v2 - v1) > 1:
                self.vary[dmIdx] = [v1, v2]
                varyRange = dm.preferenceRanking[v1:v2]
                self.varyDispVar[dmIdx].set(
                    'Varying on this range: ' + str(varyRange))
            else:
                if(v1 > v2):
                    self.varyDispVar[dmIdx].set('Start must be earlier than'
                                                ' end.')
                else:
                    self.varyDispVar[dmIdx].set('No range selected. Using '
                                                'original ranking.')
        self.event_generate('<<VaryRangeChanged>>')


class InverseContent(ttk.Frame):
    def __init__(self, master, conflict, *args):
        ttk.Frame.__init__(self, master, *args)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(7, weight=1)

        self.conflict = conflict
        self.desiredEquilibria = 0
        self.vary = [[0, 0] for dm in self.conflict.decisionMakers]

        self.desEqLab = ttk.Label(self, text='Desired Equilibrium State')
        self.desEqLab.grid(row=0, column=0, sticky=NSEW)
        self.desEqVar = StringVar()
        self.desEqSel = ttk.Combobox(self, textvariable=self.desEqVar,
                                     state='readonly')

        self.desEqSel.grid(row=0, column=1, sticky=NSEW)
        self.desEqSel.bind('<<ComboboxSelected>>', self.setDesiredEquilibrium)

        ttk.Separator(self, orient=HORIZONTAL).grid(column=0, row=1,
                                                    columnspan=2, sticky=NSEW,
                                                    pady=3)

        self.varySel = VaryRangeSelector(self, self.conflict)
        self.varySel.grid(column=0, row=2, columnspan=2, sticky=NSEW)

        ttk.Separator(self, orient=HORIZONTAL).grid(column=0, row=3,
                                                    columnspan=2, sticky=NSEW,
                                                    pady=3)

        self.calcFrame = ttk.Frame(self)
        self.calcFrame.grid(column=0, row=4, columnspan=2, sticky=NSEW)
        self.calcFrame.columnconfigure(0, weight=1)
        self.displayPermutations = StringVar(value=0)
        self.displayPermutationsChk = ttk.Checkbutton(
            self.calcFrame, text="Display all Permutations",
            variable=self.displayPermutations)
        self.displayPermutationsChk.grid(column=0, row=0, sticky=NSEW)
        self.calcButton = ttk.Button(self.calcFrame,
                                     text='Perform Inverse Calculations',
                                     command=self.refreshSolution)
        self.calcButton.grid(column=1, row=1, sticky=NSEW)
        self.permCountVar = StringVar(value='InitialVal')
        self.permCount = ttk.Label(self.calcFrame,
                                   textvariable=self.permCountVar)
        self.permCount.grid(column=0, row=1, sticky=NSEW)

        ttk.Separator(self, orient=HORIZONTAL).grid(column=0, row=5,
                                                    columnspan=2, sticky=NSEW,
                                                    pady=3)

        self.eqmChkVals = [StringVar(value=0) for x in range(4)]

        self.eqTypeFrame = ttk.Frame(self)
        self.eqTypeFrame.grid(column=0, row=6, columnspan=2, sticky=NSEW)
        ttk.Label(self.eqTypeFrame, text='Show only rankings that satisfy all '
                  'the following equilibrium concepts:').grid(column=0, row=0,
                                                              columnspan=4,
                                                              sticky=NSEW)
        self.nashChk = ttk.Checkbutton(self.eqTypeFrame, text='Nash',
                                       command=self.filter,
                                       variable=self.eqmChkVals[0])
        self.seqChk = ttk.Checkbutton(self.eqTypeFrame, text='SEQ',
                                      command=self.filter,
                                      variable=self.eqmChkVals[1])
        self.gmrChk = ttk.Checkbutton(self.eqTypeFrame, text='GMR',
                                      command=self.filter,
                                      variable=self.eqmChkVals[2])
        self.smrChk = ttk.Checkbutton(self.eqTypeFrame, text='SMR',
                                      command=self.filter,
                                      variable=self.eqmChkVals[3])
        self.nashChk.grid(column=0, row=1, sticky=NSEW, padx=(5, 10))
        self.seqChk.grid(column=1, row=1, sticky=NSEW, padx=(5, 10))
        self.gmrChk.grid(column=2, row=1, sticky=NSEW, padx=(5, 10))
        self.smrChk.grid(column=3, row=1, sticky=NSEW, padx=(5, 10))
        self.nashCountVar = StringVar(value='IV')
        self.seqCountVar = StringVar(value='IV')
        self.gmrCountVar = StringVar(value='IV')
        self.smrCountVar = StringVar(value='IV')
        self.nashCount = ttk.Label(self.eqTypeFrame,
                                   textvariable=self.nashCountVar
                                   ).grid(column=0, row=2, sticky=NSEW)
        self.seqCount = ttk.Label(self.eqTypeFrame,
                                  textvariable=self.seqCountVar
                                  ).grid(column=1, row=2, sticky=NSEW)
        self.gmrCount = ttk.Label(self.eqTypeFrame,
                                  textvariable=self.gmrCountVar
                                  ).grid(column=2, row=2, sticky=NSEW)
        self.smrCount = ttk.Label(self.eqTypeFrame,
                                  textvariable=self.smrCountVar
                                  ).grid(column=3, row=2, sticky=NSEW)

        ttk.Separator(self, orient=VERTICAL).grid(column=2, row=0, rowspan=10,
                                                  sticky=NSEW, padx=3)

        self.conditionDisp = Text(self)
        self.conditionDisp.configure(wrap="word")
        self.conditionDisp.configure(state="disabled")
        self.conditionDisp.grid(column=3, row=0, rowspan=7, sticky=NSEW)

        self.conditionDispScrl = ttk.Scrollbar(
            self, orient=VERTICAL, command=self.conditionDisp.yview)
        self.conditionDisp.configure(yscrollcommand=self.conditionDispScrl.set)
        self.conditionDispScrl.grid(column=4, row=0, rowspan=7, sticky=NSEW)

        self.resDisp = ttk.Treeview(self, selectmode='browse')

        self.resDisp.grid(column=3, row=7, rowspan=3, sticky=NSEW)

        self.resDispScrl = ttk.Scrollbar(self, orient=VERTICAL,
                                         command=self.resDisp.yview)
        self.resDisp.configure(yscrollcommand=self.resDispScrl.set)
        self.resDispScrl.grid(column=4, row=7, rowspan=3, sticky=NSEW)

        self.varySel.chgVary()

        # ###########

        self.refreshSolution()

    def refreshDisplay(self):
        headings = tuple([dm.name for dm in self.conflict.decisionMakers] +
                         ['Nash', 'SEQ', 'GMR', 'SMR'])
        self.resDisp['columns'] = headings
        for h in headings:
            self.resDisp.column(h, width=80, anchor='center', stretch=1)
            self.resDisp.heading(h, text=h)
        self.resDisp['show'] = 'headings'

        self.desEqSel['values'] = tuple(self.conflict.feasibles.ordered)
        self.desEqSel.current(0)
        self.setDesiredEquilibrium()
        self.varySel.grid_forget()
        del self.varySel
        self.varySel = VaryRangeSelector(self, self.conflict)
        self.varySel.grid(column=0, row=2, columnspan=2, sticky=NSEW)
        self.varyChange()
        self.varySel.bind('<<VaryRangeChanged>>', self.varyChange)

    def setDesiredEquilibrium(self, event=None):
        self.desiredEquilibria = self.desEqSel.current()

    def varyChange(self, *args):
        self.vary = self.varySel.vary
        varySpanSizes = [v2 - v1 for v1, v2 in self.vary if (v2 - v1) > 1]
        totalPermutations = int(np.prod([factorial(x) for x in varySpanSizes]))
        self.permCountVar.set("{} Permutations".format(totalPermutations))

    def refreshSolution(self, *args):
        self.sol = InverseSolver(self.conflict, self.vary,
                                 self.desiredEquilibria)
        self.sol.findEquilibria()
        self.filter()

    def filter(self, *args):
        filt = [bool(int(self.eqmChkVals[x].get())) for x in range(4)]
        for chld in self.resDisp.get_children():
            self.resDisp.delete(chld)

        res, counts = self.sol.filter(filt)

        if bool(int(self.displayPermutations.get())):
            for pRanki, pRank in enumerate(res):
                self.resDisp.insert('', 'end', iid=str(pRanki), values=pRank)

        self.nashCountVar.set('{} Nash'.format(counts[0]))
        self.seqCountVar.set('{} SEQ'.format(counts[1]))
        self.gmrCountVar.set('{} GMR'.format(counts[2]))
        self.smrCountVar.set('{} SMR'.format(counts[3]))

        self.conditionDisp.configure(state="normal")
        self.conditionDisp.delete("1.0", "end")
        self.conditionDisp.insert("end", "Conditions for Nash stability at "
                                  "state {}:".format(self.desEqVar.get()))
        self.conditionDisp.insert("end", self.sol.nashCond())
        self.conditionDisp.insert("end", "\n\nConditions for GMR stability at "
                                  "state {}:".format(self.desEqVar.get()))
        self.conditionDisp.insert("end", self.sol.gmrCond())
        self.conditionDisp.insert("end", "\n\nConditions for SEQ stability at "
                                  "state {}:".format(self.desEqVar.get()))
        self.conditionDisp.insert("end", self.sol.seqCond())

        self.conditionDisp.configure(state="disabled")


def main():
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    g1 = ConflictModel('pris.gmcr')

    res = InverseContent(root, g1)
    res.grid(column=0, row=0, sticky=NSEW)

    root.mainloop()


if __name__ == '__main__':
    main()
