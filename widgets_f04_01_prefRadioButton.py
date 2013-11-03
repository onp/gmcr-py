

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel


class RadiobuttonSeries(ttk.Labelframe):
    def __init__(self,master=None,text=None,width=None,*args):
        ttk.Labelframe.__init__(self,master,text=text,width=width,*args)
        self.columnconfigure(0,weight=1)

        self.varList = []
        self.stringVarList = []

        self.yLabel = ttk.Label(self,text='Y ',anchor="w")
        self.nLabel = ttk.Label(self,text='N ',anchor="w")
        self.oLabel = ttk.Label(self,text='Open',anchor="w")

        self.yLabel.grid(column=1,row=0)
        self.nLabel.grid(column=2,row=0)
        self.oLabel.grid(column=3,row=0)

        self.placeholder = False

        self.setOpts(self.varList)

    def setOpts(self,options,*args):
        if not options:
            self.placeholder = ttk.Label(self,text="This DM has no Options.")
            self.placeholder.grid(column=0,row=1,columnspan=4,sticky=(N,S,E,W))
            return None
        if self.placeholder:
            self.placeholder.grid_forget()
        self.varList=options
        self.stringVarList=[]

        for x in range(len(self.varList)):
            var = self.varList[x]
            self.stringVarList.append(StringVar(value='-'))
            yb = ttk.Radiobutton(self,variable=self.stringVarList[x],value='1',command=self.chgEvent)
            nb = ttk.Radiobutton(self,variable=self.stringVarList[x],value='0',command=self.chgEvent)
            ob = ttk.Radiobutton(self,variable=self.stringVarList[x],value='-',command=self.chgEvent)
            name = ttk.Label(self,text=var)

            yb.grid(column=1,row=int(x+1),padx=(15,10),pady=5)
            nb.grid(column=2,row=int(x+1),padx=(15,10))
            ob.grid(column=3,row=int(x+1),padx=(15,10))
            name.grid(column=0,row=int(x+1))

    def setStates(self,dashOne,*args):
        if len(dashOne) != len(self.varList):
            raise Exception('string is wrong length for setting button states')
        for x,y in enumerate(self.stringVarList):
            y.set(dashOne[x])

    def getStates(self,*args):
        dashOne = ''.join([x.get() for x in self.stringVarList])
        return dashOne

    def chgEvent(self):
        self.master.event_generate('<<RdBtnChg>>')


class RadiobuttonEntry(Frame):
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)

        self.game = game

        self.rdBtnFrame = ttk.Frame(self)
        self.rdBtnFrame.grid(column=0,row=0,columnspan=2,sticky=(N,S,E,W))

        self.entryText = StringVar(value='')

        vcmd = self.register(self.onValidate)
        self.entryBx = ttk.Entry(self,textvariable=self.entryText,validate="key",validatecommand=(vcmd,'%S','%P'))
        self.entryBx.grid(column=0,row=1,columnspan=2,sticky=(N,S,E,W))
        self.entryBx.bind('<Return>',self.generateAdd)

        self.warnText = StringVar(value='')

        self.addBtn  = ttk.Button(self,text='Add as Prefered State',command = self.generateAdd)
        self.warnLab = ttk.Label(self,textvariable=self.warnText)
        self.warnLab.grid(column=0,row=2,sticky=(N,S,E,W))
        self.addBtn.grid(column=0,row=3,columnspan=2,sticky=(N,S,E,W))

        self.reloadOpts()

    def generateAdd(self,*args):
        self.event_generate('<<AddPref>>')

    def reloadOpts(self):
        dms,options = self.game.decisionMakers,self.game.options

        self.rdBtnFrame.destroy()
        self.rdBtnFrame = ttk.Frame(self)
        self.rdBtnFrame.grid(column=0,row=0,columnspan=2,sticky=(N,S,E,W))
        self.rdBtnFrame.bind('<<RdBtnChg>>', self.rdBtnChgCmd)

        self.rdBtnSrs = []
        self.stringVarList=[]

        for x,dm in enumerate(dms):
            a = RadiobuttonSeries(self.rdBtnFrame,dm)
            self.rdBtnSrs.append(a)
            a.setOpts(options[x])
            a.grid(column=0,row=int(x),sticky=(N,S,E,W))
            self.stringVarList += a.stringVarList

        self.rdBtnChgCmd()

    def setStates(self,dashOne):
        if len(dashOne) != len(self.stringVarList):
            raise Exception('string is wrong length for setting button states: %s'%dashOne)
        for x,y in enumerate(dashOne):
            self.stringVarList[x].set(y)
        dashOne = ''.join([self.game.toYN[x] for x in dashOne])
        self.entryText.set(dashOne)

    def getStates(self):
        dashOne = ''.join([x.get() for x in self.stringVarList])
        return dashOne

    def onValidate(self,chg,res):
        if chg in ['0','1','-']:
            if len(res) < len(self.stringVarList):
                self.warnText.set('Entry too short')
                return True
            if len(res) == len(self.stringVarList):
                self.setStates(res)
                self.warnText.set('')
                return True
        else: return False

    def rdBtnChgCmd(self,*args):
        state = self.getStates()
        state = ''.join([self.game.toYN[x] for x in state])
        self.entryText.set(state)



# ######################

def main():
    root = Tk()
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)

    g1 = ConflictModel('Prisoners.gmcr')

    radFrame = RadiobuttonEntry(root,g1)
    radFrame.grid(column=0,row=0,sticky=(N,W))

    root.mainloop()

    print(radFrame.getStates())


if __name__ == '__main__':
    main()