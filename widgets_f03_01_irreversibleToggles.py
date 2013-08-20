
from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel


class ToggleButton(ttk.Labelframe):
    def __init__(self,master=None,optNumber=0,name='option',*args):
        ttk.Frame.__init__(self,master,*args)
        self.columnconfigure(0,weight=1)

        self.fwdIcon=PhotoImage(file='icons/fwdArrow.gif')
        self.backIcon=PhotoImage(file='icons/backArrow.gif')
        self.bothIcon=PhotoImage(file='icons/bothArrow.gif')

        self.optNum = optNumber

        ttk.Label(self,text=name).grid(column=0,row=0,sticky=(N,S,E,W))
        ttk.Label(self,text='  N  ').grid(column=1,row=0,sticky=(N,S,E,W))
        ttk.Label(self,text='  Y  ').grid(column=3,row=0,sticky=(N,S,E,W))

        self.fwd = ttk.Button(self,image=self.fwdIcon,  command=lambda: self.chg('0'))
        self.back = ttk.Button(self,image=self.backIcon,command=lambda: self.chg('-'))
        self.both = ttk.Button(self,image=self.bothIcon,command=lambda: self.chg('1'))

        self.both.grid(column=2,row=0,sticky=(N,S,E,W))

        self.curr = self.both

        self.irrev = '-'

    def chg(self,new):
        self.curr.grid_remove()
        if new == '0':
            self.back.grid(column=2,row=0,sticky=(N,S,E,W))
            self.curr= self.back
            self.irrev='0'
        elif new == '1':
            self.fwd.grid(column=2,row=0,sticky=(N,S,E,W))
            self.curr= self.fwd
            self.irrev='1'
        elif new == '-':
            self.both.grid(column=2,row=0,sticky=(N,S,E,W))
            self.curr= self.both
            self.irrev='-'
        self.master.master.master.event_generate('<<IrrevChange>>')

    def getIrrev(self):
        if self.irrev != '-':
            return (self.optNum,self.irrev)


class IrreversibleSetter(Frame):
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)


        self.opts= []
        self.game = game

        self.mainFrame = ttk.Frame(self)
        self.mainFrame.grid(column=0,row=0,sticky=(N,S,E,W))
        self.mainFrame.columnconfigure(0,weight=1)

        self.refreshDisplay()

        self.bind('<<IrrevChange>>',self.irrevChg)

    def refreshDisplay(self):
        self.opts=[]
        for chld in self.mainFrame.winfo_children():
            chld.destroy()
        optcnt=0
        for dmi,dm in enumerate(self.game.dmList):
            currframe = ttk.LabelFrame(self.mainFrame,text=dm)
            currframe.grid(column=0,row=dmi,sticky=(N,S,E,W))
            currframe.columnconfigure(0,weight=1)
            for movei,move in enumerate(self.game.optList[dmi]):
                newtog = ToggleButton(currframe,optcnt,move)
                newtog.grid(column=0,row=movei,sticky=(N,S,E,W))
                self.opts.append(newtog)
                optcnt+=1
        for optNum,direction in self.game.irrev:
            self.opts[optNum].chg(direction)


    def irrevChg(self,*args):
        irrev = []
        for opt in self.opts:
            if opt.getIrrev(): irrev.append(opt.getIrrev())
        self.game.setIrrev(irrev)





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