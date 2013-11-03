

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel
from data_02_conflictSolvers import LogicalSolver


class LogResultDisp(ttk.Frame):
    toYN = {'0':'N','1':'Y','-':'-'}

    def __init__(self,master,game,*args):
        ttk.Frame.__init__(self,master,*args)
        self.columnconfigure(3,weight=1)
        self.rowconfigure(0,weight=1)
        self.rowconfigure(3,weight=1)

        self.game = game
        
        if self.game.numDMs() > 0:
            self.dmVar     = StringVar(value = self.game.decisionMakers[0].name)
            self.stateVar  = StringVar(value = self.game.feasDec[0])
        else:
            self.dmVar     = StringVar()
            self.stateVar  = StringVar()
            
        self.eqTypeVar = StringVar(value = 'Nash')

        self.resDisp = ttk.Treeview(self)
        headings = ('Ordered','Decimal','Binary','Nash','GMR','SEQ','SIM','SEQ & SIM','SMR')
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

        self.RMdumpBtnJSON = ttk.Button(self.dumpframe,text='Save Reachability as JSON',command=lambda: self.sol.saveJSON())
        self.RMdumpBtnJSON.grid(column=0,row=0,sticky=(N,S,E,W),padx=3,pady=3)

        self.RMdumpBtnCSV = ttk.Button(self.dumpframe,text='Save Reachability as npz',command=lambda: self.sol.saveMatrices())
        self.RMdumpBtnCSV.grid(column=1,row=0,sticky=(N,S,E,W),padx=3,pady=3)

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

        self.refreshSolution()

    def refreshDisplay(self):
        self.dmVar.set(self.game.dmList[0])
        self.dmSel['values'] = tuple(self.game.dmList)
        self.stateVar.set(self.game.feasDec[0])
        self.stateSel['values'] = tuple(self.game.feasDec)

    def chgState(self,event):
        eqType = int(self.resDisp.identify("column",event.x,event.y).strip('#'))
        stateNum = self.resDisp.index(self.resDisp.selection())

        self.stateVar.set(self.game.feasDec[stateNum])
        if eqType <=3:
            self.eqTypeVar.set('Nash')
        elif eqType ==4:
            self.eqTypeVar.set('GMR')
        elif eqType ==5:
            self.eqTypeVar.set('SEQ')
        elif eqType ==6:
            self.eqTypeVar.set('SIM')
        elif eqType ==4:
            self.eqTypeVar.set('SMR')

        self.refreshNarration()


    def refreshSolution(self):
        if self.game.numDMs() <= 0:
            return None
        self.sol = LogicalSolver(self.game)
        self.sol.findEquilibria()
        for chld in self.resDisp.get_children():
            self.resDisp.delete(chld)
        for state in self.game.feasDec:
            values = tuple([self.game.ordered[state],state, ''.join([self.toYN[y] for y in self.game.dec2bin(state)])]+
                           [x for x in self.sol.allEquilibria[:,state]])
            self.resDisp.insert('','end',iid=str(state),text=str(state),values=values)

        self.refreshNarration()


    def refreshNarration(self,*args):
        eqCalcDict={'Nash':self.sol.nash,
                    'GMR':self.sol.gmr,
                    'SEQ':self.sol.seq,
                    'SIM':self.sol.sim,
                    'SMR':self.sol.smr}
        self.equilibriumNarrator.delete('1.0','end')
        dm = self.game.dmList.index(self.dmVar.get())
        state = int(self.stateVar.get())
        eqType = self.eqTypeVar.get()
        newText = eqCalcDict[eqType](dm,state)[1]
        self.equilibriumNarrator.insert('1.0',newText)


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
