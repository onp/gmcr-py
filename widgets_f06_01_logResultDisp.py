# Copyright:   (c) Oskar Petersons 2013

"""Widgets for displaying a conflict's equilibria.

Loaded by the frame_06_equilibria module.
"""

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel
from data_02_conflictSolvers import LogicalSolver
from visualizerLauncher import launchVis


class LogResultDisp(ttk.Frame):
    toYN = {'0':'N','1':'Y','-':'-'}

    def __init__(self,master,game,*args):
        ttk.Frame.__init__(self,master,*args)
        self.columnconfigure(3,weight=1)
        self.rowconfigure(0,weight=1)
        self.rowconfigure(3,weight=1)

        self.game = game
        
        self.dmVar = StringVar()
        self.stateVar = StringVar()
            
        self.eqTypeVar = StringVar()

        self.resDisp = ttk.Treeview(self)
        headings = ('Ordered','Decimal','YN','Nash','GMR','SEQ','SIM','SEQ & SIM','SMR')
        self.resDisp['columns'] = headings
        for h in headings:
            self.resDisp.column(h,width=80,anchor='center',stretch=1)
            self.resDisp.heading(h,text=h)
        self.resDisp['show'] = 'headings'
        self.resDisp.grid(column=0,row=0,columnspan=4,sticky=(N,S,E,W))

        self.resDispScrl = ttk.Scrollbar(self, orient=VERTICAL,command = self.resDisp.yview)
        self.resDisp.configure(yscrollcommand=self.resDispScrl.set)
        self.resDispScrl.grid(column=4,row=0,sticky=(N,S,E,W))

        ttk.Separator(self,orient=HORIZONTAL).grid(column=0,row=1,columnspan=10,sticky=(N,S,E,W),pady=3)

        self.dmSel = ttk.Combobox(self,textvariable=self.dmVar,state='readonly')
        self.dmSel.grid(column=0,row=2,sticky=(N,S,E,W),padx=3,pady=3)

        self.stateSel = ttk.Combobox(self,textvariable=self.stateVar,state='readonly')
        self.stateSel.grid(column=1,row=2,sticky=(N,S,E,W),padx=3,pady=3)

        self.eqTypeSel = ttk.Combobox(self,textvariable=self.eqTypeVar,state='readonly')
        self.eqTypeSel['values'] = ('Nash','GMR','SEQ','SIM','SMR')
        self.eqTypeSel.grid(column=2,row=2,sticky=(N,S,E,W),padx=3,pady=3)

        self.dumpframe = ttk.Frame(self)
        self.dumpframe.grid(column=3,row=2,sticky=(N,S,E))

        self.RMdumpBtnJSON = ttk.Button(self.dumpframe,text='Save Reachability as JSON',command=self.saveToJSON)
        self.RMdumpBtnJSON.grid(column=0,row=0,sticky=(N,S,E,W),padx=3,pady=3)
        self.visLaunchBtn = ttk.Button(self.dumpframe,text='Launch Visualizer',command=self.loadVis)
        self.visLaunchBtn.grid(column=1,row=0,sticky=(N,S,E,W),padx=3,pady=3)

        self.equilibriumNarrator = Text(self, wrap='word')
        self.equilibriumNarrator.grid(column=0,row=3,columnspan=4,sticky=(N,S,E,W))

        self.eqNarrScrl = ttk.Scrollbar(self, orient=VERTICAL,command = self.resDisp.yview)
        self.equilibriumNarrator.configure(yscrollcommand=self.eqNarrScrl.set)
        self.eqNarrScrl.grid(column=4,row=3,sticky=(N,S,E,W))

        # ###########
        self.dmSel.bind('<<ComboboxSelected>>',self.refreshNarration)
        self.stateSel.bind('<<ComboboxSelected>>',self.refreshNarration)
        self.eqTypeSel.bind('<<ComboboxSelected>>',self.refreshNarration)
        self.resDisp.bind('<Button-1>',self.chgState)

        self.refreshDisplay()
        self.refreshSolution()

    def refreshDisplay(self):
        self.dmSel['values'] = tuple([dm.name for dm in self.game.decisionMakers])
        self.dmSel.current(0)
        self.stateSel['values'] = tuple(self.game.feasibles.ordered)
        self.stateSel.current(0)
        self.eqTypeSel.current(0)

    def chgState(self,event):
        eqType = int(self.resDisp.identify("column",event.x,event.y).strip('#'))
        stateNum = self.resDisp.index(self.resDisp.selection())
        self.stateVar.set(self.game.feasibles.ordered[stateNum])
        
        if eqType <=4:
            self.eqTypeVar.set('Nash')
        elif eqType ==5:
            self.eqTypeVar.set('GMR')
        elif eqType ==6:
            self.eqTypeVar.set('SEQ')
        elif eqType ==7:
            self.eqTypeVar.set('SIM')
        elif eqType >=8:
            self.eqTypeVar.set('SMR')

        self.refreshNarration()

    def refreshSolution(self):
        self.sol = LogicalSolver(self.game)
        self.sol.findEquilibria()
        for chld in self.resDisp.get_children():
            self.resDisp.delete(chld)
        for state in range(len(self.game.feasibles.decimal)):
            values = tuple([self.game.feasibles.ordered[state],self.game.feasibles.decimal[state], self.game.feasibles.yn[state]]+
                           [x if x == True else '' for x in self.sol.allEquilibria[:,state]])
            self.resDisp.insert('','end',iid=str(state),text=str(state),values=values)

        self.refreshNarration()

    def refreshNarration(self,*args):
        eqCalcDict={'Nash':self.sol.nash,
                    'GMR':self.sol.gmr,
                    'SEQ':self.sol.seq,
                    'SIM':self.sol.sim,
                    'SMR':self.sol.smr}
        self.equilibriumNarrator.delete('1.0','end')
        dm = self.game.decisionMakers[self.dmSel.current()]
        state = self.stateSel.current()
        eqType = self.eqTypeVar.get()
        newText = eqCalcDict[eqType](dm,state)[1]
        self.equilibriumNarrator.insert('1.0',newText)
        
    def saveToJSON(self,event=None):
        fileName = filedialog.asksaveasfilename(defaultextension= '.json',
                                        filetypes = (("JSON files", "*.json")
                                                     ,("All files", "*.*") ),
                                        parent=self)
        if fileName:
            self.sol.saveJSON(fileName)
                                        
    def loadVis(self,event=None):
        self.sol.saveJSON("webVis/json/visData.json")
        launchVis()

def main():
    root = Tk()
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)

    g1 = ConflictModel('Prisoners.gmcr')


    res = LogResultDisp(root,g1)
    res.grid(column=0,row=0,sticky=(N,S,E,W))


    root.mainloop()

if __name__ == '__main__':
    main()
