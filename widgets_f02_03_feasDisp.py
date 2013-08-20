

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel


class FeasDisp(ttk.Frame):
    def __init__(self,master=None,game=None,*args):
        ttk.Frame.__init__(self,master,padding=5)
        self.columnconfigure(1,weight=1)
        self.rowconfigure(2,weight=1)

        self.game = game

        self.dispFormat = StringVar(value='pattern')
        self.dispList = StringVar()
        self.feasList = []

        self.fmts = {'Pattern':'YN-','List (binary)':'YN','List (ordered and [decimal])':'ord_dec'}
        cBoxOpts =('Pattern','List (binary)','List (ordered and [decimal])')
        self.feasText = ttk.Label(self,text = 'Feasible States').grid(row=0,column=0,columnspan=3)
        self.cBox    = ttk.Combobox(self,textvariable=self.dispFormat,values=cBoxOpts,state='readonly')
        self.cBoxLb  = ttk.Label(self,text='Format:')
        self.feasLBx = Listbox(self,listvariable=self.dispList)
        self.scrl    = ttk.Scrollbar(self, orient=VERTICAL,command = self.feasLBx.yview)

        # ###########
        self.cBoxLb.grid(column=0,row=1,sticky=(N,S,E,W),pady=3)
        self.cBox.grid(column=1,row=1,columnspan=2,sticky=(N,S,E,W),pady=3)
        self.feasLBx.grid(column=0,row=2,columnspan=2,sticky=(N,S,E,W))
        self.scrl.grid(column=2,row=2,sticky=(N,S,E,W))

        self.cBox.bind('<<ComboboxSelected>>',self.fmtSel)
        self.feasLBx.configure(yscrollcommand=self.scrl.set)

        self.dispFormat.set('Pattern')
        self.fmtSel()


    def fmtSel(self,*args):
        self.refreshList()


    def setFeas(self,feasList):
        self.feasList = feasList
        self.refreshList()

    def refreshList(self):
        fmt = self.fmts[self.dispFormat.get()]
        feas = sorted(self.game.getFeas(fmt))
        #formatting operation needs to happen. fetch view from game?
        self.dispList.set(tuple(feas))



def main():
    root = Tk()
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)

    g1 = ConflictModel('Prisoners.gmcr')

    FeasView = FeasDisp(root,g1)
    FeasView.grid(column=0,row=0,sticky=(N,S,E,W))


    root.mainloop()

if __name__ == '__main__':
    main()
