from tkinter import *
from tkinter import ttk

class PreferenceRanking(ttk.Frame):
    def __init__(self,master,game,dmIdx):
        ttk.Frame.__init__(self,master,borderwidth=2)

        self.game = game
        self.dmIdx = dmIdx
        self.dmText = StringVar(value=self.game.dmList[dmIdx]+': ')
        self.dmLabel = ttk.Label(self,textvariable=self.dmText)
        self.dmLabel.grid(row=0,column=0,sticky=(N,S,E,W))
        self.prefRankText = StringVar(value=str(self.game.rankPreferences(self.dmIdx)))
        self.prefRank = ttk.Label(self,textvariable=self.prefRankText,relief="sunken")
        self.prefRank.grid(row=0,column=1,sticky=(N,S,E,W))
        self.selectBtn = ttk.Button(self,text="Edit",command=self.selectCmd)
        self.selectBtn.grid(row=0,column=2,sticky=(N,S,E,W))

        self.columnconfigure(1,weight=1)

    def update(self,*args):
        self.prefRankText.set(str(self.game.prefRank(self.dmIdx)))

    def selectCmd(self,*args):
        self.event_generate('<<DMselect>>',x=self.dmIdx)

    def deselect(self,*args):
        self.configure(relief='flat')


class PreferenceRankingMaster(ttk.Frame):
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)
        self.game = game
        self.cframe = ttk.Frame(self)
        self.columnconfigure(0,weight=1)
        self.cframe.columnconfigure(0,weight=1)
        self.dmIdx=0
        if len(self.game.decisionMakers) > 0:
            self.refresh()

    def update(self):
        for ranking in self.rankings:
            ranking.update()

    def chgDM(self,event):
        self.rankings[self.dmIdx].deselect()
        self.dmIdx = event.x
        self.rankings[self.dmIdx].configure(relief='raised')
        self.event_generate('<<DMchg>>',x=event.x)

    def refresh(self):
        self.cframe.destroy()
        self.cframe = ttk.Frame(self)
        self.cframe.grid(row=0,column=0,sticky=(N,S,E,W))
        self.cframe.columnconfigure(0,weight=1)
        self.rankings = []
        for idx in range(self.game.numDMs()):
            self.rankings.append(PreferenceRanking(self.cframe,self.game,idx))
            self.rankings[-1].grid(row=idx,column=0,padx=3,pady=3,sticky=(N,S,E,W))
            self.rankings[-1].bind('<<DMselect>>',self.chgDM)
        self.rankings[self.dmIdx].configure(relief='raised')


class PreferenceEditDisplay(ttk.Frame):
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)

        self.game = game
        self.disp = ttk.Treeview(self, columns=('state','weight'))
        self.scrl = ttk.Scrollbar(self, orient=VERTICAL,command = self.disp.yview)
        self.upBtn   = ttk.Button(self,width=10,text='Up',     command = self.upCmd  )
        self.downBtn = ttk.Button(self,width=10,text='Down',   command = self.downCmd)
        self.delBtn  = ttk.Button(self,width=10,text='Delete', command = self.delCmd)
        self.dmIdx = 0
        self.selIdx = None
        self.selId = None

        # ##########

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0,weight=1)

        self.disp.heading('state', text='Preferred Condition')
        self.disp.heading('weight', text='Weighting')
        self.disp['show'] = 'headings'

        self.disp.grid(column=0,row=0,columnspan=5,sticky=(N,S,E,W))
        self.scrl.grid(column=5,row=0,sticky=(N,S,E,W))
        self.disp.configure(yscrollcommand=self.scrl.set)

        self.upBtn.grid(column=2,row=2,sticky=(N,S,E,W))
        self.downBtn.grid(column=3,row=2,sticky=(N,S,E,W))
        self.delBtn.grid(column=4,row=2,sticky=(N,S,E,W))

        self.disp.bind('<<TreeviewSelect>>', self.selChgCmd)

    def refresh(self):
        """Fully refreshes the list displayed"""
        for child in self.disp.get_children():
            self.disp.delete(child)
        if self.dmIdx is not None:
            for i,x in enumerate(self.game.prefPri[self.dmIdx]):
                self.disp.insert('','end',x,text=x)
                self.disp.set(x,'state',''.join([self.game.toYN[y] for y in x]))
                self.disp.set(x,'weight',str(2**(len(self.game.prefPri[self.dmIdx])-i-1)))

    def changeDM(self,dmIdx):
        """Changes which Decision Maker is displayed."""
        self.dmIdx = dmIdx
        self.refresh()

    def selChgCmd(self,*args):
        """Called whenever the selection changes."""
        self.selId  = self.disp.selection()
        self.selIdx = self.disp.index(self.selId)
        self.event_generate('<<SelItem>>',x=self.selIdx)

    def upCmd(self,*args):
        """Called whenever an item is moved upwards."""
        idx = self.selIdx
        if (idx !=0) and (self.dmIdx is not None):
            self.game.movePreference(self.dmIdx,idx,idx-1)
            self.event_generate('<<ValueChange>>')
            self.disp.selection_set(self.selId)
            self.selChgCmd()

    def downCmd(self,*args):
        """Called whenever an item is moved downwards."""
        idx = self.selIdx
        if (idx != len(self.game.prefPri[self.dmIdx])-1) and (self.dmIdx is not None):
            self.game.movePreference(self.dmIdx,idx,idx+1)
            self.event_generate('<<ValueChange>>')
            self.disp.selection_set(self.selId)
            self.selChgCmd()

    def delCmd(self,*args):
        """Called when an item is deleted."""
        idx = self.selIdx
        self.game.removePreference(self.dmIdx,idx)
        self.event_generate('<<ValueChange>>')
        try:
            self.disp.selection_set(self.game.prefPri[self.dmIdx][idx])
        except IndexError:
            try:
                self.disp.selection_set(self.game.prefPri[self.dmIdx][idx-1])
            except IndexError:
                self.selIdx = None


class PreferenceLongDisp(ttk.Frame):
    toYN = {'0':'N','1':'Y','-':'-'}

    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)

        self.game = game
        self.disp = ttk.Treeview(self,columns=('state','bin','payoff'))
        self.scrl = ttk.Scrollbar(self, orient=VERTICAL,command = self.disp.yview)
        self.dmIdx = 0

        # ##########

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)

        self.disp.heading('state',text='Ordered State')
        self.disp.heading('bin',text='Binary')
        self.disp.heading('payoff',text='Payoff')
        self.disp['show'] = 'headings'

        self.disp.grid(column=0,row=0,columnspan=5,sticky=(N,S,E,W))
        self.scrl.grid(column=5,row=0,sticky=(N,S,E,W))
        self.disp.configure(yscrollcommand=self.scrl.set)

    def refresh(self):
        """Fully refreshes the list displayed"""
        for child in self.disp.get_children():
            self.disp.delete(child)
        if self.dmIdx is not None:
            for i,x in enumerate(self.game.getFeas('dec')):
                self.disp.insert('','end',text=x,values=(str(self.game.ordered[x])+' '+
                                 ''.join([self.toYN[y] for y in self.game.dec2bin(x)])+
                                 ' '+str(self.game.payoffs[self.dmIdx][x])))


    def changeDM(self,dmIdx):
        """Changes which Decision Maker is displayed."""
        self.dmIdx = dmIdx
        self.refresh()