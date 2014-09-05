# Copyright:   (c) Oskar Petersons 2013

"""Widgets for selecting a state using radio buttons for each option.

Loaded by the frame_04_preferencePrioritization module.
Nearly a clone of widgets_f02_01_radioButtonEntry.
"""

from tkinter import *
from tkinter import ttk
from data_01_conflictModel import ConflictModel
import re


class RadiobuttonSeries(ttk.Labelframe):
    """State entry for a single decision maker"""
    def __init__(self,master=None,text=None,width=None,*args):
        ttk.Labelframe.__init__(self,master,text=text,width=width,*args)
        self.columnconfigure(0,weight=1)

        self.options = []
        self.stringVarList = []

        self.yLabel = ttk.Label(self,text='Y ',anchor="w")
        self.nLabel = ttk.Label(self,text='N ',anchor="w")
        self.oLabel = ttk.Label(self,text='Open',anchor="w")

        self.yLabel.grid(column=1,row=0)
        self.nLabel.grid(column=2,row=0)
        self.oLabel.grid(column=3,row=0)

        self.placeholder = False

        self.setOpts(self.options)

    def setOpts(self,options,*args):
        if not options:
            self.placeholder = ttk.Label(self,text="This DM has no Options.")
            self.placeholder.grid(column=0,row=1,columnspan=4,sticky=(N,S,E,W))
            return None
        if self.placeholder:
            self.placeholder.grid_forget()
        self.options=options
        self.stringVarList=[]

        for idx,opt in enumerate(self.options):
            self.stringVarList.append(StringVar(value='-'))
            yb = ttk.Radiobutton(self,variable=self.stringVarList[idx],value='Y',command=self.chgEvent)
            nb = ttk.Radiobutton(self,variable=self.stringVarList[idx],value='N',command=self.chgEvent)
            ob = ttk.Radiobutton(self,variable=self.stringVarList[idx],value='-',command=self.chgEvent)
            name = ttk.Label(self,text=opt.name)

            yb.grid(column=1,row=int(idx+1),padx=(15,10),pady=5)
            nb.grid(column=2,row=int(idx+1),padx=(15,10))
            ob.grid(column=3,row=int(idx+1),padx=(15,10))
            name.grid(column=0,row=int(idx+1))

    def getStates(self,*args):
        states = []
        for idx,bit in enumerate([x.get() for x in self.stringVarList]):
            if bit != '-':
                states.append( (self.options[idx],bit) )
        return states

    def chgEvent(self):
        self.master.event_generate('<<RdBtnChg>>')
        
    def disable(self):
        for child in self.winfo_children():
            child['state'] = 'disabled'

    def enable(self):
        for child in self.winfo_children():
            child['state'] = 'normal'

class RadiobuttonEntry(Frame):
    """State entry for the entire conflict, as a set of RadioButtonSeries elements."""
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)

        self.game = game
        
        self.rbeCanvas = Canvas(self)
        self.rdBtnFrame = ttk.Frame(self.rbeCanvas)
        self.scrollY = ttk.Scrollbar(self, orient=VERTICAL,command = self.rbeCanvas.yview)

        self.rbeCanvas.grid(column=0,row=0,columnspan=2,sticky=(N,S,E,W))
        self.scrollY.grid(column=2,row=0,sticky=(N,S,E,W))
        self.rbeCanvas.configure(yscrollcommand=self.scrollY.set)
        self.canvWindow = self.rbeCanvas.create_window((0,0),window=self.rdBtnFrame,anchor='nw')
        
        self.rowconfigure(0, weight=1)

        self.entryText = StringVar(value='')

        vcmd = self.register(self.onValidate)
        self.entryBx = ttk.Entry(self,textvariable=self.entryText,validate="key",validatecommand=(vcmd,'%S','%P'))
        self.entryBx.grid(column=0,row=1,sticky=(N,S,E,W))
        self.entryBx.bind('<Return>',self.generateAdd)

        self.warnText = StringVar(value='')
        self.warnLab = ttk.Label(self,textvariable=self.warnText,width=18)
        self.warnLab.grid(column=1,row=1,sticky=(N,S,E,W))
        
        self.codeText = StringVar(value='')
        
        vcmd2 = self.register(self.onValidate2)
        self.codeBx = ttk.Entry(self,textvariable=self.codeText,validate="key",validatecommand=(vcmd2,'%S','%P'))
        self.codeBx.grid(column=0,row=2,sticky=(N,S,E,W))
        self.codeBx.bind('<Return>',self.generateAdd)
        
        self.warnText2 = StringVar(value='')
        self.warnLab2 = ttk.Label(self,textvariable=self.warnText2)
        self.warnLab2.grid(column=1,row=2,sticky=(N,S,E,W))

        self.addBtn  = ttk.Button(self,text='Add as Prefered State',command = self.generateAdd)
        self.stageBtn = ttk.Button(self,text='Add to Staging',command = self.generateStage)

        self.addBtn.grid(column=0,row=4,columnspan=2,sticky=(N,S,E,W))
        self.stageBtn.grid(column=0,row=5,columnspan=2,sticky=(N,S,E,W))
        
        self.isDisabled = False
        
        self.columnconfigure(0,weight=1)

        self.reloadOpts()
        
        self.regexValidChars = re.compile(r'^[-\d, fi]*$')
        self.regexStatesIf = re.compile(r'^ *(-)?(\d+) *iff? *(-)?(\d+) *$')
        self.regexStates = re.compile(r' *(-)?(\d+) *')
        
        self.hasValidIf = False
        
    
        
    def resize(self,event=None):
        self.rbeCanvas.configure(scrollregion=self.rbeCanvas.bbox("all"))

    def generateAdd(self,event=None):
        self.event_generate('<<AddPref>>')
        
    def generateStage(self,event=None):
        self.event_generate('<<StagePref>>')

    def reloadOpts(self):
        self.rbeCanvas.delete(self.canvWindow)
        self.rdBtnFrame.destroy()
        self.rdBtnFrame = ttk.Frame(self.rbeCanvas)
        self.canvWindow = self.rbeCanvas.create_window((0,0),window=self.rdBtnFrame,anchor='nw')
        self.rdBtnFrame.bind('<<RdBtnChg>>', self.rdBtnChgCmd)
        self.rdBtnFrame.bind("<Configure>",self.resize)

        self.rdBtnSrs = []
        self.stringVarList=[]

        for x,dm in enumerate(self.game.decisionMakers):
            a = RadiobuttonSeries(self.rdBtnFrame,dm)
            self.rdBtnSrs.append(a)
            a.setOpts(dm.options)
            a.grid(column=0,row=int(x),sticky=(N,S,E,W))
            self.stringVarList += a.stringVarList

        self.rdBtnChgCmd()
        
        if self.isDisabled:
            self.disable()
        
    def disable(self,event=None):
        self.isDisabled = True
        self.entryBx['state'] = 'disabled'
        self.codeBx['state'] = 'disabled'
        self.addBtn['state'] = 'disabled'
        self.stageBtn['state'] = 'disabled'
        for srs in self.rdBtnSrs:
            srs.disable()

    def enable(self,event=None):
        self.isDisabled = False
        self.entryBx['state'] = 'normal'
        self.codeBx['state'] = 'normal'
        self.addBtn['state'] = 'normal'
        self.stageBtn['state'] = 'normal'
        for srs in self.rdBtnSrs:
            srs.enable()

    def setStates(self,dashOne):
        if dashOne == 'clear':
            for var in self.stringVarList:
                var.set('-')
            self.entryText.set('-'*len(self.stringVarList))
            return
        if len(dashOne) != len(self.stringVarList):
            raise Exception('string is wrong length for setting button states: %s'%dashOne)
        for x,y in enumerate(dashOne):
            self.stringVarList[x].set(y)
        self.entryText.set(dashOne)

    def getStates(self):
        states = []
        for srs in self.rdBtnSrs:
            states.extend(srs.getStates())
        return states

    def onValidate(self,chg,res):
        if chg in ['Y','N','y','n','-']:
            if len(res) < len(self.stringVarList):
                self.warnText.set('Entry too short')
                return True
            if len(res) == len(self.stringVarList):
                self.setStates(res.upper())
                self.warnText.set('')
                return True
        return False

    def onValidate2(self,chg,res):
        if self.regexValidChars.match(res):
            if "if" in res:
                m = self.regexStatesIf.match(res)
                if m:
                    self.warnText2.set('')
                    self.handleIf(res,m.groups())
                else:
                    self.warnText2.set('Invalid')
            else:
                states = res.split(',')
                sts2 = []
                print('states:')
                for st in states:
                    m = self.regexStates.match(st)
                    if m:
                        sts2.append(m.groups())
                    else:
                        self.warnText2.set('Invalid')
                        return True
                self.warnText2.set('')
                setTo = '-'*len(self.stringVarList)
                for neg,st in sts2:
                    if int(st)>len(self.stringVarList):
                        self.warnText2.set(st+' is too large')
                        return True
                    if setTo[int(st)-1] != "-":
                        self.warnText2.set("Too many "+st+"s")
                        return True
                    print(neg,st)
                    if neg:
                        setTo = setTo[:(int(st)-1)]+'N'+setTo[int(st):]
                    else:
                        setTo = setTo[:(int(st)-1)]+'Y'+setTo[int(st):]
                self.setStates(setTo)
            
            return True
        self.warnText2.set('Invalid')
        return False
        
    def handleIf(self,string,states):
        # q if p ( equivalent to 'If p, then q' )
        print(states)
        if int(states[1])>len(self.stringVarList):
            self.warnText2.set(states[1]+' is too large')
            return True
        elif int(states[3])>len(self.stringVarList):
            self.warnText2.set(states[3]+' is too large')
            return True
        elif states[1] == states[3]:
            self.warnText2.set("duplicate")
            return True
        
        q  = [int(states[1]-1),"N" if states[0] else "Y")
        nq = [int(states[1]-1),"Y" if states[0] else "N")   # not q
        p = [int(states[3]-1),"N" if states[2] else "Y")
        np = [int(states[3]-1),"Y" if states[2] else "N")   # not p
        
        newCondition = None

        if "iff" in string:
            newCondition = self.game.newCompoundCondition([[p,q],[np,nq]])
        else:
            newCondition = self.game.newCompoundCondition([[p,q],[np,q],[np,nq]])
        
        
    def rdBtnChgCmd(self,*args):
        val = ''.join([x.get() for x in self.stringVarList])
        self.entryText.set(val)
        self.warnText.set('')
        
        val = [[i+1,x.get()] for i,x in enumerate(self.stringVarList) if (x.get() != "-")]
        outVar = []
        for i,x in val:
            if x == "N":
                outVar.append("-"+str(i))
            else:
                outVar.append(str(i))
        
        self.codeText.set(", ".join(outVar))
        
        self.warnText2.set('')



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