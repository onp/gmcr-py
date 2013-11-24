# Copyright:   (c) Oskar Petersons 2013

"""Editable listbox widgets used in editing DMs and options.

Loaded by the frame_01_decisionMakers module.
"""

from tkinter import *
from tkinter import ttk

class ListInput(ttk.Frame):
    """Listbox, with a linked entry box."""
    def __init__(self,master=None,lHeight=None,*args):
        ttk.Frame.__init__(self,master,*args)

        self.listVariable = StringVar(value=tuple(['Double Click to Add Item']))
        self.entryBxVar   = StringVar(value='')
        self.listDisp     = Listbox(self,listvariable=self.listVariable,height=lHeight,width=40)
        self.scrl         = ttk.Scrollbar(self, orient=VERTICAL,command = self.listDisp.yview)
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



    def linkOwner(self,var,areDMs=False):
        """Links the listbox content to 'var'.  If 'areDMs' is not false,
        the items in var will be treated as DMs with attached options.
        """
        self.owner = var
        if areDMs:
            self.areDMs = True
        self.listVariable.set(tuple([x.name for x in self.owner]+['Double Click to Add Item']))
        for idx in range(len(self.owner)):
            self.listDisp.itemconfigure(idx, foreground='black')
        self.listDisp.itemconfigure(len(self.owner), foreground='#A0A0A0')


    def moveEntry(self,idx,idx2):
        """Moves an item from idx to idx2."""
        self.owner.insert(idx2,self.owner.pop(idx))
        self.listVariable.set(tuple([x.name for x in self.owner]+['Double Click to Add Item']))
        self.listDisp.selection_clear(idx)
        self.listDisp.selection_set(idx2)
        self.selChgCmd()
        self.event_generate("<<breakingChange>>")

    def upCmd(self,*args):
        """Moves the selected element up one space in the list"""
        idx = self.listDisp.selIdx
        if idx not in [-1,0,len(self.owner)]:   #check that there is an entry selected, and it isn't the first entry.
            self.moveEntry(idx,idx-1)

    def downCmd(self,*args):
        """Moves the selected element down one space in the list."""
        idx = self.listDisp.selIdx
        if idx not in [-1,len(self.owner)-1,len(self.owner)]:   #check that there is an entry selected, and it isn't the last entry
            self.moveEntry(idx,idx+1)

    def delCmd(self,*args):
        """Deletes the selected element from the list."""
        idx = self.listDisp.selIdx
        if idx != len(self.owner):
            del self.owner[idx]
            self.listVariable.set(tuple([x.name for x in self.owner]+['Double Click to Add Item']))
            self.listDisp.itemconfigure(len(self.owner), foreground='#A0A0A0')
        self.event_generate("<<breakingChange>>")

    def selChgCmd(self,*args):
        """Called when the selection changes."""
        self.listDisp.selIdx = int(self.listDisp.curselection()[0])
        self.event_generate('<<Sel2>>')

    def editCmd(self,*args):
        """Called when a list entry is selected for editing."""
        try:
            self.entryBxVar.set(self.owner[self.listDisp.selIdx].name)
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
            if (idx == len(self.owner)):
                self.owner.append(newItem)
                self.listDisp.itemconfigure(idx, foreground='black')
                self.event_generate("<<breakingChange>>")
            else:
                self.owner[idx].name=newItem
            self.listVariable.set(tuple([x.name for x in self.owner]+['Double Click to Add Item']))
            self.listDisp.itemconfigure(len(self.owner), foreground='#A0A0A0')
        self.tempEntry.unbind('<FocusOut>')
        self.tempEntry.unbind('<Return>')
        self.tempEntry.state(['disabled'])
        self.entryBxVar.set('')
        self.listDisp.focus_set()
        self.listDisp.selection_clear(0,'end')
        self.listDisp.selection_set(self.listDisp.selIdx)
        self.selChgCmd()




# ####################     testing

from data_01_conflictModel import ConflictModel

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


