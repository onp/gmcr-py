# Copyright:   (c) Oskar Petersons 2013

"""Widgets for editing the reversibility of options in the conflict.

Loaded by the frame_03_irreversibles module.
"""

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel


class ToggleButton(ttk.Labelframe):
    def __init__(self,master,option,*args):
        ttk.Frame.__init__(self,master,*args)
        self.columnconfigure(0,weight=1)
        
        self.option = option

        self.fwdIcon=PhotoImage(file='icons/fwdArrow.gif')
        self.backIcon=PhotoImage(file='icons/backArrow.gif')
        self.bothIcon=PhotoImage(file='icons/bothArrow.gif')

        ttk.Label(self,text=option.name).grid(column=0,row=0,sticky=(N,S,E,W))
        ttk.Label(self,text='  N  ').grid(column=1,row=0,sticky=(N,S,E,W))
        ttk.Label(self,text='  Y  ').grid(column=3,row=0,sticky=(N,S,E,W))

        self.fwd = ttk.Button(self,image=self.fwdIcon,  command=lambda: self.chg('back'))
        self.back = ttk.Button(self,image=self.backIcon,command=lambda: self.chg('both'))
        self.both = ttk.Button(self,image=self.bothIcon,command=lambda: self.chg('fwd'))

        self.both.grid(column=2,row=0,sticky=(N,S,E,W))
        self.curr = self.both
        
        self.chg(option.permittedDirection)

    def chg(self,new):
        self.curr.grid_remove()
        if new == 'back':
            self.back.grid(column=2,row=0,sticky=(N,S,E,W))
            self.curr= self.back
            self.option.permittedDirection = 'back'
        elif new == 'fwd':
            self.fwd.grid(column=2,row=0,sticky=(N,S,E,W))
            self.curr = self.fwd
            self.option.permittedDirection = 'fwd'
        elif new == 'both':
            self.both.grid(column=2,row=0,sticky=(N,S,E,W))
            self.curr= self.both
            self.option.permittedDirection = 'both'


class IrreversibleSetter(Frame):
    def __init__(self,master,conflict):
        ttk.Frame.__init__(self,master)

        self.opts= []
        self.conflict = conflict
        
        self.canv = Canvas(self)

        self.mainFrame = ttk.Frame(self.canv)
        self.scrollY = ttk.Scrollbar(self, orient=VERTICAL,command = self.canv.yview)
        self.canvWindow = self.canv.create_window((0,0),window=self.mainFrame,anchor='nw')

        self.canv.grid(column=0,row=0,sticky=(N,S,E,W))
        self.scrollY.grid(column=1,row=0,sticky=(N,S,E,W))
        self.canv.configure(yscrollcommand=self.scrollY.set)
        
        self.rowconfigure(0, weight=1)
        self.mainFrame.bind("<Configure>",self.resize)

        self.refreshDisplay()
        
    def resize(self,event=None):
        self.canv.configure(scrollregion=self.canv.bbox("all"))

    def refreshDisplay(self):
        self.opts=[]
        for chld in self.mainFrame.winfo_children():
            chld.destroy()
        for dmIdx,dm in enumerate(self.conflict.decisionMakers):
            currframe = ttk.LabelFrame(self.mainFrame,text=dm.name)
            currframe.grid(column=0,row=dmIdx,sticky=(N,S,E,W))
            currframe.columnconfigure(0,weight=1)
            for optIdx,opt in enumerate(dm.options):
                newtog = ToggleButton(currframe,opt)
                newtog.grid(column=0,row=optIdx,sticky=(N,S,E,W))
                self.opts.append(newtog)






# ######################

def main():
    root = Tk()
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)

    g1 = ConflictModel('Prisoners.gmcr')

    f1 = IrreversibleSetter(root,g1)
    f1.grid(column=0,row=0,sticky=(N,S,E,W))

    root.mainloop()


if __name__ == '__main__':
    main()