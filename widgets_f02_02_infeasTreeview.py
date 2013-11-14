from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel



class TreeInfeas(ttk.Frame):
    def __init__(self,master,game=None,*args):
        ttk.Frame.__init__(self,master,padding=(5))

        self.game = game

        self.tDisp = ttk.Treeview(self, columns=('state','stDes','stRem'))
        self.scrl       = ttk.Scrollbar(self, orient=VERTICAL,command = self.tDisp.yview)

        self.upBtn   = ttk.Button(self,width=10,text='Up',     command = self.upCmd  )
        self.downBtn = ttk.Button(self,width=10,text='Down',   command = self.downCmd)
        self.delBtn  = ttk.Button(self,width=10,text='Delete', command = self.delCmd)

        # ##########

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0,weight=1)

        self.tDisp.heading('state', text='Infeasible State')
        self.tDisp.heading('stDes', text='# of States Described')
        self.tDisp.heading('stRem', text='# of States Removed')
        self.tDisp['show'] = 'headings'

        self.tDisp.grid(column=0, row=0, columnspan=5, sticky=(N,S,E,W))
        self.scrl.grid(column=5,row=0,sticky=(N,S,E,W))
        self.tDisp.configure(yscrollcommand=self.scrl.set)

        self.upBtn.grid(  column=2,row=2, sticky=(N,S,E,W))
        self.downBtn.grid(column=3,row=2, sticky=(N,S,E,W))
        self.delBtn.grid( column=4,row=2, sticky=(N,S,E,W))

        self.tDisp.bind('<<TreeviewSelect>>', self.selChgCmd)

        self.refreshView()


    def refreshView(self):
        """Fully refreshes the list displayed"""
        chldn = self.tDisp.get_children()
        for chld in chldn:
            self.tDisp.delete(chld)
        if len(self.game.infeasibles)>0:
            self.game.recalculateFeasibleStates()
        for infeas in self.game.infeasibles:
            key = infeas.ynd()
            self.tDisp.insert('','end',key,text=key)
            self.tDisp.set(key,'state',key)
            self.tDisp.set(key,'stDes',str(2**(key.count('-'))))
            self.tDisp.set(key,'stRem',str(infeas.statesRemoved))


    def selChgCmd(self,*args):
        """Called whenever the selection changes."""
        self.tDisp.selId  = self.tDisp.selection()
        self.tDisp.selIdx = self.tDisp.index(self.tDisp.selId)
        self.event_generate('<<SelItem>>',x=self.tDisp.selIdx)

    def upCmd(self,*args):
        """Called whenever an item is moved upwards."""
        idx = self.tDisp.selIdx
        if idx !=0:
            self.game.infeasibles.moveCondition(idx,idx-1)
            self.game.recalculateFeasibleStates()
            self.event_generate('<<ValueChange>>')
            self.tDisp.selection_set(self.tDisp.selId)
            self.selChgCmd()

    def downCmd(self,*args):
        """Called whenever an item is moved downwards."""
        idx = self.tDisp.selIdx
        if idx != len(self.game.infeasibles)-1:
            self.game.infeasibles.moveCondition(idx,idx+1)
            self.game.recalculateFeasibleStates()
            self.event_generate('<<ValueChange>>')
            self.tDisp.selection_set(self.tDisp.selId)
            self.selChgCmd()

    def delCmd(self,*args):
        """Called when an item is deleted."""
        idx = self.tDisp.selIdx
        self.game.infeasibles.removeCondition(idx)
        self.game.recalculateFeasibleStates()
        self.event_generate('<<ValueChange>>')
        if self.game.infeasibles:
            try:
                self.tDisp.selection_set(self.game.infeasibles[idx].ynd())
            except IndexError:
                self.tDisp.selection_set(self.game.infeasibles[idx-1].ynd())


def main():
    root = Tk()
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)

    g1 = ConflictModel('AmRv2.gmcr')

    theTree = TreeInfeas(root,g1)
    theTree.grid(column=0,row=0,sticky=(N,S,E,W))


    root.mainloop()

if __name__ == '__main__':
    main()
