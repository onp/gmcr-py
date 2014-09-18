# Copyright:   (c) Oskar Petersons 2013

"""Widgets displaying the results of Inverse Approach analysis.

Loaded by the frame_07_inverseApproach module.
"""

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel
from data_02_conflictSolvers import InverseSolver
import numpy as np
from math import factorial

class VaryRangeSelector(ttk.Frame):
    def __init__(self,master,game,*args):
        ttk.Frame.__init__(self,master,*args)

        self.game = game
        self.vary=[[0,0] for dm in self.game.decisionMakers]

        self.varyVar = []
        self.varyDispVar = []

        for dmIdx,dm in enumerate(self.game.decisionMakers):
            dmFrame  = ttk.Labelframe(self,text=dm.name)
            dmFrame.grid(column=0,row=dmIdx)

            startVar = StringVar()
            endVar   = StringVar()
            dispVar  = StringVar(value='No range selected. Using original ranking.')
            ttk.Label(dmFrame,text='Original ranking: '+ str(dm.preferenceRanking)).grid(column=0,row=1,columnspan=4,sticky=(N,S,E,W))
            ttk.Label(dmFrame,textvariable=dispVar).grid(column=0,row=2,columnspan=4,sticky=(N,S,E,W))

            ttk.Label(dmFrame,text='Vary from:').grid(column=0,row=0)
            startSel = ttk.Combobox(dmFrame,textvariable=startVar,state='readonly')
            startSel['values'] = tuple(dm.preferenceRanking)
            startSel.current(0)
            startSel.grid(column=1,row=0)
            startSel.bind('<<ComboboxSelected>>',self.chgVary)

            ttk.Label(dmFrame,text='  to:').grid(column=2,row=0)
            endSel = ttk.Combobox(dmFrame,textvariable=endVar,state='readonly')
            endSel['values'] = tuple(dm.preferenceRanking)
            endSel.current(0)
            endSel.grid(column=3,row=0)
            endSel.bind('<<ComboboxSelected>>',self.chgVary)

            self.varyVar.append([startVar,endVar])
            self.varyDispVar.append(dispVar)

    def chgVary(self,*args):
        self.vary=[[0,0] for dm in self.game.decisionMakers]
        for dmIdx,rangeForDM in enumerate(self.varyVar):
            dm = self.game.decisionMakers[dmIdx]
            v1 = dm.preferenceRanking.index(eval(rangeForDM[0].get()))
            v2 = dm.preferenceRanking.index(eval(rangeForDM[1].get()))+1
            if (v2-v1)>1:
                self.vary[dmIdx] = [v1,v2]
                varyRange = dm.preferenceRanking[v1:v2]
                self.varyDispVar[dmIdx].set('Varying on this range: '+str(varyRange))
            else:
                if(v1>v2):
                    self.varyDispVar[dmIdx].set('Start must be earlier than end.')
                else:
                    self.varyDispVar[dmIdx].set('No range selected. Using original ranking.')
        self.event_generate('<<VaryRangeChanged>>')


class InverseContent(ttk.Frame):
    def __init__(self,master,game,*args):
        ttk.Frame.__init__(self,master,*args)
        self.columnconfigure(3,weight=1)
        self.rowconfigure(7,weight=1)

        self.game = game
        self.desiredEquilibria = 0
        self.vary = [[0,0] for dm in self.game.decisionMakers]

        self.desEqLab = ttk.Label(self,text='Desired Equilibrium State')
        self.desEqLab.grid(row=0,column=0,sticky=(N,S,E,W))
        self.desEqVar = StringVar()
        self.desEqSel = ttk.Combobox(self,textvariable=self.desEqVar,state='readonly')

        self.desEqSel.grid(row=0,column=1,sticky=(N,S,E,W))
        self.desEqSel.bind('<<ComboboxSelected>>', self.setDesiredEquilibrium)

        ttk.Separator(self,orient=HORIZONTAL).grid(column=0,row=1,columnspan=2,sticky=(N,S,E,W),pady=3)

        self.varySel = VaryRangeSelector(self,self.game)
        self.varySel.grid(column=0,row=2,columnspan=2,sticky=(N,S,E,W))

        ttk.Separator(self,orient=HORIZONTAL).grid(column=0,row=3,columnspan=2,sticky=(N,S,E,W),pady=3)

        self.calcFrame = ttk.Frame(self)
        self.calcFrame.grid(column=0,row=4,columnspan=2,sticky=(N,S,E,W))
        self.calcFrame.columnconfigure(0,weight=1)
        self.displayPermutations = StringVar(value=0)
        self.displayPermutationsChk = ttk.Checkbutton(self.calcFrame,text = "Display all Permutations",variable=self.displayPermutations)
        self.displayPermutationsChk.grid(column=0,row=0,sticky=(N,S,E,W))
        self.calcButton = ttk.Button(self.calcFrame,text='Perform Inverse Calculations',command=self.refreshSolution)
        self.calcButton.grid(column=1,row=1,sticky=(N,S,E,W))
        self.permCountVar = StringVar(value='InitialVal')
        self.permCount = ttk.Label(self.calcFrame,textvariable = self.permCountVar)
        self.permCount.grid(column=0, row=1, sticky=(N,S,E,W))

        ttk.Separator(self,orient = HORIZONTAL).grid(column=0, row=5,columnspan=2,sticky=(N,S,E,W),pady=3)

        self.eqmChkVals = [StringVar(value=0) for x in range(4)]

        self.eqTypeFrame = ttk.Frame(self)
        self.eqTypeFrame.grid(column=0,row=6,columnspan=2,sticky=(N,S,E,W))
        ttk.Label(self.eqTypeFrame,text='Show only rankings that satisfy all the following equilibrium concepts:').grid(column=0,row=0,columnspan=4,sticky=(N,S,E,W))
        self.nashChk = ttk.Checkbutton(self.eqTypeFrame,text='Nash',command=self.filter,variable=self.eqmChkVals[0])
        self.seqChk  = ttk.Checkbutton(self.eqTypeFrame,text='SEQ', command=self.filter,variable=self.eqmChkVals[1])
        self.gmrChk  = ttk.Checkbutton(self.eqTypeFrame,text='GMR', command=self.filter,variable=self.eqmChkVals[2])
        self.smrChk  = ttk.Checkbutton(self.eqTypeFrame,text='SMR', command=self.filter,variable=self.eqmChkVals[3])
        self.nashChk.grid(column=0,row=1,sticky=(N,S,E,W),padx=(5,10))
        self.seqChk.grid( column=1,row=1,sticky=(N,S,E,W),padx=(5,10))
        self.gmrChk.grid( column=2,row=1,sticky=(N,S,E,W),padx=(5,10))
        self.smrChk.grid( column=3,row=1,sticky=(N,S,E,W),padx=(5,10))
        self.nashCountVar = StringVar(value='IV')
        self.seqCountVar  = StringVar(value='IV')
        self.gmrCountVar  = StringVar(value='IV')
        self.smrCountVar  = StringVar(value='IV')
        self.nashCount = ttk.Label(self.eqTypeFrame,textvariable=self.nashCountVar).grid(column=0,row=2,sticky=(N,S,E,W))
        self.seqCount  = ttk.Label(self.eqTypeFrame,textvariable=self.seqCountVar).grid(column=1,row=2,sticky=(N,S,E,W))
        self.gmrCount  = ttk.Label(self.eqTypeFrame,textvariable=self.gmrCountVar).grid(column=2,row=2,sticky=(N,S,E,W))
        self.smrCount  = ttk.Label(self.eqTypeFrame,textvariable=self.smrCountVar).grid(column=3,row=2,sticky=(N,S,E,W))

        ttk.Separator(self,orient=VERTICAL).grid(column=2,row=0,rowspan=10,sticky=(N,S,E,W),padx=3)
        
        
        self.conditionDisp = Text(self)
        self.conditionDisp.configure(wrap="word")
        self.conditionDisp.configure(state="disabled")
        self.conditionDisp.grid(column=3,row=0,rowspan=7,sticky=(N,S,E,W))
        
        self.conditionDispScrl = ttk.Scrollbar(self,orient=VERTICAL,command=self.conditionDisp.yview)
        self.conditionDisp.configure(yscrollcommand=self.conditionDispScrl.set)
        self.conditionDispScrl.grid(column=4,row=0,rowspan=7,sticky=(N,S,E,W))
        
        
        self.resDisp = ttk.Treeview(self)

        self.resDisp.grid(column=3,row=7,rowspan=3,sticky=(N,S,E,W))

        self.resDispScrl = ttk.Scrollbar(self, orient=VERTICAL,command = self.resDisp.yview)
        self.resDisp.configure(yscrollcommand=self.resDispScrl.set)
        self.resDispScrl.grid(column=4,row=7,rowspan=3,sticky=(N,S,E,W))
        

        
        self.varySel.chgVary()

        # ###########

        self.refreshSolution()

    def refreshDisplay(self):
        headings = tuple([dm.name for dm in self.game.decisionMakers]+['Nash','SEQ','GMR','SMR'])
        self.resDisp['columns'] = headings
        for h in headings:
            self.resDisp.column(h,width=80,anchor='center',stretch=1)
            self.resDisp.heading(h,text=h)
        self.resDisp['show'] = 'headings'

        self.desEqSel['values'] = tuple(self.game.feasibles.ordered)
        self.desEqSel.current(0)
        self.setDesiredEquilibrium()
        self.varySel.grid_forget()
        del self.varySel
        self.varySel = VaryRangeSelector(self,self.game)
        self.varySel.grid(column=0,row=2,columnspan=2,sticky=(N,S,E,W))
        self.varyChange()
        self.varySel.bind('<<VaryRangeChanged>>',self.varyChange)

    def setDesiredEquilibrium(self,event=None):
        self.desiredEquilibria = self.desEqSel.current()
    
        
    def varyChange(self,*args):
        self.vary = self.varySel.vary
        varySpanSizes = [v2-v1 for v1,v2 in self.vary if (v2-v1)>1]
        totalPermutations = int(np.prod([factorial(x) for x in varySpanSizes]))
        self.permCountVar.set("%s Permutations"%totalPermutations)

    def refreshSolution(self,*args):
        self.sol = InverseSolver(self.game,self.vary,self.desiredEquilibria)
        self.sol.findEquilibria()
        self.filter()

    def filter(self,*args):
        filt = [bool(int(self.eqmChkVals[x].get())) for x in range(4)]
        for chld in self.resDisp.get_children():
            self.resDisp.delete(chld)

        res,counts = self.sol.filter(filt)
        
        if bool(int(self.displayPermutations.get())):
            for pRanki,pRank in enumerate(res):
                self.resDisp.insert('','end',iid=str(pRanki),values=pRank)
                
        self.nashCountVar.set('%s Nash'%counts[0])
        self.seqCountVar.set('%s SEQ'%counts[1])
        self.gmrCountVar.set('%s GMR'%counts[2])
        self.smrCountVar.set('%s SMR'%counts[3])
        
        self.conditionDisp.configure(state="normal")
        self.conditionDisp.delete("1.0","end")
        self.conditionDisp.insert("end","Conditions for Nash stability at state %s:"%(self.desEqVar.get()))
        self.conditionDisp.insert("end",self.sol.nashCond())
        self.conditionDisp.insert("end","\n\nConditions for GMR stability at state %s:"%(self.desEqVar.get()))
        self.conditionDisp.insert("end",self.sol.gmrCond())
        self.conditionDisp.insert("end","\n\nConditions for SEQ stability at state %s:"%(self.desEqVar.get()))
        self.conditionDisp.insert("end",self.sol.seqCond())
        
        self.conditionDisp.configure(state="disabled")


def main():
    root = Tk()
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)

    g1 = ConflictModel('pris.gmcr')


    res = InverseContent(root,g1)
    res.grid(column=0,row=0,sticky=(N,S,E,W))


    root.mainloop()

if __name__ == '__main__':
    main()
