# Copyright:   (c) Oskar Petersons 2013

"""Various widgets used in editing and displaying prioritization-based preferences.

Loaded by the frame_04_preferencePrioritization module.
"""

from tkinter import *
from tkinter import ttk
import data_03_gmcrUtilities as gmcrUtil

class PreferenceRanking(ttk.Frame):
    """Displays the state ranking for a single DM, and allows that DM to be selected."""
    def __init__(self,master,game,dm,idx):
        ttk.Frame.__init__(self,master,borderwidth=2)

        self.game = game
        self.dm = dm
        self.dmIdx = idx
        self.dmText = StringVar(value = dm.name + ': ')
        self.dmLabel = Label(self,textvariable=self.dmText)
        self.dmLabel.grid(row=0,column=0,sticky=(N,S,E,W))
        self.prefRankText = StringVar(value=str(dm.preferenceVector))
        self.prefRank = ttk.Label(self,textvariable=self.prefRankText,relief="sunken")
        self.prefRank.grid(row=0,column=1,sticky=(N,S,E,W))
        self.selectBtn = ttk.Button(self,text="Edit",command=self.selectCmd)
        self.selectBtn.grid(row=0,column=2,sticky=(N,S,E,W))

        self.columnconfigure(1,weight=1)

    def update(self,*args):
        self.prefRankText.set('still not implemented') #str(self.game.prefRank(self.dmIdx)))

    def selectCmd(self,*args):
        self.event_generate('<<DMselect>>',x=self.dmIdx)

    def deselect(self,*args):
        self.configure(relief='flat')
        self.dmLabel.configure(bg="SystemButtonFace")
        
    def select(self,*args):
        self.configure(relief='raised')
        print(self.dmLabel['background'])
        self.dmLabel.configure(bg="green")
        print(self.winfo_class())

class PreferenceRankingMaster(ttk.Frame):
    """Displays a PreferenceRanking widget for each DM."""
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)
        self.game = game
        self.cframe = ttk.Frame(self)
        self.columnconfigure(0,weight=1)
        self.cframe.columnconfigure(0,weight=1)
        self.dmSelIdx = None
        
        self.clearBtn = ttk.Button(self,text="Clear Selection",command=self.clearSel)
        self.clearBtn.grid(row=1,column=0,sticky=(N,S,E,W))
        
        self.refresh()

    def update(self):
        for ranking in self.rankings:
            ranking.update()

    def chgDM(self,event):
        if self.dmSelIdx is not None:
            self.rankings[self.dmSelIdx].deselect()
        self.dmSelIdx = event.x
        self.rankings[self.dmSelIdx].select()
        self.dm = self.game.decisionMakers[event.x]
        self.event_generate('<<DMchg>>')

    def refresh(self):
        self.cframe.destroy()
        self.cframe = ttk.Frame(self)
        self.cframe.grid(row=0,column=0,sticky=(N,S,E,W))
        self.cframe.columnconfigure(0,weight=1)
        self.rankings = []
        for idx,dm in enumerate(self.game.decisionMakers):
            self.rankings.append(PreferenceRanking(self.cframe,self.game,dm,idx))
            self.rankings[-1].grid(row=idx,column=0,padx=3,pady=3,sticky=(N,S,E,W))
            self.rankings[-1].bind('<<DMselect>>',self.chgDM)
        if self.dmSelIdx is not None:
            self.rankings[self.dmSelIdx].select()
        
        if self.game.useManualPreferenceVectors:
            for ranking in self.rankings:
                ranking.selectBtn['state'] = 'disabled'

    def clearSel(self,event=None):
        self.rankings[self.dmSelIdx].deselect()
        self.dmSelIdx = None
        self.dm = None
        self.event_generate('<<DMchg>>')

class PreferenceEditDisplay(ttk.Frame):
    """Displays the preference statements for the selected DM."""
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)

        self.game = game
        self.disp = ttk.Treeview(self, columns=('state','weight'))
        self.scrl = ttk.Scrollbar(self, orient=VERTICAL,command = self.disp.yview)
        self.upBtn   = ttk.Button(self,width=10,text='Up',     command = self.upCmd  )
        self.downBtn = ttk.Button(self,width=10,text='Down',   command = self.downCmd)
        self.delBtn  = ttk.Button(self,width=10,text='Delete', command = self.delCmd)
        self.dm = self.game.decisionMakers[0]
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
        if self.dm is not None:
            self.dm.weightPreferences()
            for pref in self.dm.preferences:
                key  = pref.ynd()
                self.disp.insert('','end',key,text=key)
                self.disp.set(key,'state',key)
                self.disp.set(key,'weight',pref.weight)
        
        if self.game.useManualPreferenceVectors:
            self.disp['selectmode'] = 'none'
            self.upBtn['state'] = 'disabled'
            self.downBtn['state'] = 'disabled'
            self.delBtn['state'] = 'disabled'
        else:
            self.disp['selectmode'] = 'browse'
            self.upBtn['state'] = 'normal'
            self.downBtn['state'] = 'normal'
            self.delBtn['state'] = 'normal'

    def changeDM(self,dm):
        """Changes which Decision Maker is displayed."""
        self.dm = dm
        self.refresh()

    def selChgCmd(self,*args):
        """Called whenever the selection changes."""
        self.selId  = self.disp.selection()
        self.selIdx = self.disp.index(self.selId)
        self.event_generate('<<SelItem>>',x=self.selIdx)

    def upCmd(self,*args):
        """Called whenever an item is moved upwards."""
        idx = self.selIdx
        if (idx !=0) and (self.dm is not None):
            self.dm.preferences.moveCondition(idx,idx-1)
            self.event_generate('<<ValueChange>>')
            self.disp.selection_set(self.selId)
            self.selChgCmd()

    def downCmd(self,*args):
        """Called whenever an item is moved downwards."""
        idx = self.selIdx
        if (idx != len(self.dm.preferences)-1) and (self.dm is not None):
            self.dm.preferences.moveCondition(idx,idx+1)
            self.event_generate('<<ValueChange>>')
            self.disp.selection_set(self.selId)
            self.selChgCmd()

    def delCmd(self,*args):
        """Called when an item is deleted."""
        idx = self.selIdx
        self.dm.preferences.removeCondition(idx)
        self.event_generate('<<ValueChange>>')
        try:
            self.disp.selection_set(self.dm.preferences[idx].ynd())
        except IndexError:
            try:
                self.disp.selection_set(self.dm.preferences[idx-1].ynd())
            except IndexError:
                self.selIdx = None


class PreferenceLongDisp(ttk.Frame):
    toYN = {'0':'N','1':'Y','-':'-'}

    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)

        self.game = game
        self.disp = ttk.Treeview(self,columns=('state','yn','payoff'))
        self.scrl = ttk.Scrollbar(self, orient=VERTICAL,command = self.disp.yview)
        self.dm = self.game.decisionMakers[0]

        # ##########

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)

        self.disp.heading('state',text='Ordered State')
        self.disp.heading('yn',text='YN notation')
        self.disp.heading('payoff',text='Payoff')
        self.disp['show'] = 'headings'

        self.disp.grid(column=0,row=0,columnspan=5,sticky=(N,S,E,W))
        self.scrl.grid(column=5,row=0,sticky=(N,S,E,W))
        self.disp.configure(yscrollcommand=self.scrl.set)

    def refresh(self):
        """Fully refreshes the list displayed"""
        for child in self.disp.get_children():
            self.disp.delete(child)
        if self.dm is not None:
            for state in range(len(self.game.feasibles.decimal)):
                self.disp.insert('','end',text=state,
                        values=(str(self.game.feasibles.ordered[state]) + ' '
                                +str(self.game.feasibles.yn[state]) + ' '
                                +str(self.dm.payoffs[state])))
                                 
        if self.game.useManualPreferenceVectors:
            self.disp['selectmode'] = 'none'


    def changeDM(self,dm):
        """Changes which Decision Maker is displayed."""
        self.dm = dm
        self.refresh()