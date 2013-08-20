# trying to generate a framework for the editable boxes

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel



class ListInput(ttk.Frame):
    """Listbox, with a linked entry box."""
    def __init__(self,master=None,lHeight=None,*args):
        ttk.Frame.__init__(self,master,*args)

        self.lVarExt2 = None

        self.lVar       = StringVar(value=tuple(['Double Click to Add Item']))
        self.entryBxVar = StringVar(value='')
        self.listDisp   = Listbox(self,listvariable=self.lVar,height=lHeight,width=40)
        self.scrl       = ttk.Scrollbar(self, orient=VERTICAL,command = self.listDisp.yview)
        self.listDisp.configure(yscrollcommand=self.scrl.set)

        self.upBtn   = ttk.Button(self,width=10,text='Up',     command = self.upCmd  )
        self.downBtn = ttk.Button(self,width=10,text='Down',   command = self.downCmd)
        self.delBtn  = ttk.Button(self,width=10,text='Delete', command = self.delCmd)

        self.tempEntry = ttk.Entry(self,textvariable=self.entryBxVar)

        self.listDisp.selIdx = -1
        self.editIdx   = -1

        # ##########

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0,weight=1)

        self.listDisp.grid(column=0, row=0, columnspan=5, sticky=(N,S,E,W))
        self.scrl.grid(column=5,row=0,sticky=(N,S,E,W))

        self.upBtn.grid(  column=2,row=2, sticky=(N,S,E,W))
        self.downBtn.grid(column=3,row=2, sticky=(N,S,E,W))
        self.delBtn.grid( column=4,row=2, sticky=(N,S,E,W))

        self.tempEntry.grid(column=2, row=3,columnspan=3, sticky=(N,S,E,W))
        self.tempEntry.state(['disabled'])

        self.listDisp.bind('<<ListboxSelect>>', self.selChgCmd)
        self.listDisp.bind('<Double-1>', self.editCmd)
        self.listDisp.bind('<Delete>', self.delCmd)
        self.listDisp.bind('<Return>', self.editCmd)



    def linkVar(self,var,var2=None):
        """Links the listbox content to 'var'.  If 'var2' is defined, it will be
        treated as lists of the children of each element of 'var'."""
        self.lVarExt = var
        self.lVarExt2 = var2
        self.lVar.set(tuple(self.lVarExt+['Double Click to Add Item']))
        for idx in range(len(self.lVarExt)):
            self.listDisp.itemconfigure(idx, foreground='black')
        self.listDisp.itemconfigure(len(self.lVarExt), foreground='#A0A0A0')
        self.event_generate('<<Chg>>')


    def moveEntry(self,idx,idx2):
        self.lVarExt.insert(idx2,self.lVarExt.pop(idx))
        if self.lVarExt2:
            self.lVarExt2.insert(idx2,self.lVarExt2.pop(idx))
        self.lVar.set(tuple(self.lVarExt+['Double Click to Add Item']))
        self.listDisp.selection_clear(idx)
        self.listDisp.selection_set(idx2)
        self.selChgCmd()

    def upCmd(self,*args):
        """Moves the selected element up one space in the list"""
        idx = self.listDisp.selIdx
        if idx not in [-1,0,len(self.lVarExt)]:
            self.moveEntry(idx,idx-1)

    def downCmd(self,*args):
        """Moves the selected element down one space in the list."""
        idx = self.listDisp.selIdx
        if idx not in [-1,len(self.lVarExt)-1,len(self.lVarExt)]:
            self.moveEntry(idx,idx+1)

    def delCmd(self,*args):
        """Deletes the selected element from the list."""
        idx = self.listDisp.selIdx
        if idx != len(self.lVarExt):
            self.lVarExt.__delitem__(idx)
            self.lVarExt2.__delitem__(idx)
            self.lVar.set(tuple(self.lVarExt+['Double Click to Add Item']))
            self.listDisp.itemconfigure(len(self.lVarExt), foreground='#A0A0A0')
        self.event_generate('<<Chg>>')

    def selChgCmd(self,*args):
        """Called when the selection changes."""
        self.listDisp.selIdx = int(self.listDisp.curselection()[0])
        self.event_generate('<<Sel2>>')

    def editCmd(self,*args):
        """Called when a list entry is selected for editting."""
        try:
            self.entryBxVar.set(self.lVarExt[self.listDisp.selIdx])
        except IndexError:
            self.entryBxVar.set('')
        self.tempEntry.state(['!disabled'])
        self.listDisp.selection_set(self.listDisp.selIdx)
        self.editIdx=self.listDisp.selIdx
        self.tempEntry.focus_set()
        self.tempEntry.selection_range(0,'end')
        self.tempEntry.bind('<FocusOut>', lambda x: self.svChgCmd(self.entryBxVar.get(),self.editIdx))
        self.tempEntry.bind('<Return>',   lambda x: self.svChgCmd(self.entryBxVar.get(),self.editIdx))


    def svChgCmd(self,newItem,idx):
        """Called when leaving the entry box. Updates the relevant list entry."""
        if newItem:
            if (idx == len(self.lVarExt)):
                self.lVarExt.append(newItem)
                if self.lVarExt2 is not None:
                    self.lVarExt2.append([])
                self.listDisp.itemconfigure(idx, foreground='black')
            else:
                self.lVarExt[idx]=newItem
            self.lVar.set(tuple(self.lVarExt+['Double Click to Add Item']))
            self.listDisp.itemconfigure(len(self.lVarExt), foreground='#A0A0A0')
        self.tempEntry.unbind('<FocusOut>')
        self.tempEntry.unbind('<Return>')
        self.tempEntry.state(['disabled'])
        self.entryBxVar.set('')
        self.listDisp.focus_set()
        self.event_generate('<<Chg>>')
        self.listDisp.selection_clear(0,'end')
        self.listDisp.selection_set(self.listDisp.selIdx)
        self.selChgCmd()








# ####################     running the program

def main():
    root = Tk()
    root.columnconfigure(0,weight=1)
    root.columnconfigure(2,weight=2)
    root.rowconfigure(0,weight=1)

    theNewBox1 = ListInput(root,lHeight=30)
    theNewBox1.grid(column=0,row=0,sticky=(N,S,E,W))

    g1 = ConflictModel('AmRv2.gmcr')

    theNewBox1.linkVar(g1.dmList)


    root.mainloop()

    print(g1.dmList)



if __name__ == '__main__':
    main()


