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
        
        if len(game.feasibles)<1000:
            self.prefRankText = StringVar(value=str(dm.preferenceVector))
        else:
            self.prefRankText = StringVar(value="Too Many States")
        self.prefRank = ttk.Label(self,textvariable=self.prefRankText,relief="sunken")
        self.prefRank.grid(row=1,column=0,sticky=(N,S,E,W))
        
        self.selectBtn = ttk.Button(self,text="Edit",command=self.selectCmd)
        self.selectBtn.grid(row=0,column=1,rowspan=2,sticky=(N,S,E,W))

        self.columnconfigure(0,weight=1)

    def update(self,*args):
        self.prefRankText.set('still not implemented') #str(self.game.prefRank(self.dmIdx)))

    def selectCmd(self,*args):
        self.event_generate('<<DMselect>>',x=self.dmIdx)

    def deselect(self,*args):
        self.configure(relief='flat')
        self.dmLabel.configure(bg="SystemButtonFace")
        
    def select(self,*args):
        self.configure(relief='raised')
        self.dmLabel.configure(bg="green")

class PreferenceRankingMaster(ttk.Frame):
    """Displays a PreferenceRanking widget for each DM."""
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)
        self.game = game
        self.cframe = ttk.Frame(self)
        self.columnconfigure(0,weight=1)
        self.cframe.columnconfigure(0,weight=1)
        self.dmSelIdx = None
        self.dm = None
        
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
                
    def disable(self,event=None):
        for ranking in self.rankings:
            ranking.selectBtn['state'] = 'disabled'
        self.clearBtn['state'] = 'disabled'
            
    def enable(self,event=None):
        for ranking in self.rankings:
            ranking.selectBtn['state'] = 'normal'    
        self.clearBtn['state'] = 'normal'
            
    def clearSel(self,event=None):
        if self.dmSelIdx is not None:
            self.rankings[self.dmSelIdx].deselect()
        self.dmSelIdx = None
        self.dm = None
        self.event_generate('<<DMchg>>')
        
class PreferenceStaging(ttk.Frame):
    """Displays the conditions that make up a compound condition."""
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)

        self.game = game
        
        self.label = ttk.Label(self,text="Staging")
        self.listDisp = ttk.Treeview(self)
        self.scrollY = ttk.Scrollbar(self,orient=VERTICAL,command = self.listDisp.yview)
        self.listDisp.configure(yscrollcommand=self.scrollY.set)
        self.removeConditionBtn = ttk.Button(self,text="Remove Condition from Staging",command=self.removeCondition)
        self.addToPreferencesBtn = ttk.Button(self,text="Add to Preferences ->",command=self.addToPreferences)
        
        self.columnconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        
        self.label.grid(column=0,row=0,sticky=(N,S,E,W))
        self.listDisp.grid(column=0,row=1,sticky=(N,S,E,W))
        self.scrollY.grid(column=1,row=1,sticky=(N,S,E,W))
        self.removeConditionBtn.grid(column=0,row=2,sticky=(N,S,E,W))
        self.addToPreferencesBtn.grid(column=0,row=3,sticky=(N,S,E,W))
        
        self.listDisp.bind('<<TreeviewSelect>>', self.selChgCmd)
        self.clear()
        
    def clear(self):
        self.conditionList = self.game.newCompoundCondition([])
        self.selId  = None
        self.selIdx = None
        
        for child in self.listDisp.get_children():
            self.listDisp.delete(child)
        self.removeConditionBtn['state'] = 'disabled'
        self.addToPreferencesBtn['state'] = 'disabled'
            
    def selChgCmd(self,*args):
        """Called whenever the selection changes."""
        self.selId  = self.listDisp.selection()
        self.selIdx = self.listDisp.index(self.selId)
        self.event_generate('<<SelCond>>',x=self.selIdx)
        
    def setList(self,newConditions):
        self.clear()
        if newConditions.isCompound:
            self.conditionList = newConditions
        else:
            self.conditionList.append(newConditions)

        for ynd in self.conditionList.name.split(', '):
            self.listDisp.insert('','end',text=ynd)
            
        if len(self.conditionList)>0:
            self.removeConditionBtn['state'] = 'normal'
            self.addToPreferencesBtn['state'] = 'normal'
        
    def removeCondition(self,event=None):
        if self.selIdx is not None:
            del self.conditionList[self.selIdx]
            self.listDisp.delete(self.selId)
            
            if len(self.conditionList) == 0:
                self.removeConditionBtn['state'] = 'disabled'
                self.addToPreferencesBtn['state'] = 'disabled'
        
    def addToPreferences(self,event=None):
        self.event_generate('<<PullFromStage>>')
        
    def addCondition(self,condition):
        self.conditionList.append(condition)
        self.listDisp.insert('','end',text=condition.name)
        
        if len(self.conditionList)>0:
            self.removeConditionBtn['state'] = 'normal'
            self.addToPreferencesBtn['state'] = 'normal'
        
    def disable(self,event=None):
        self.removeConditionBtn['state'] = 'disabled'
        self.addToPreferencesBtn['state'] = 'disabled'
        
    def enable(self,event=None):
        self.removeConditionBtn['state'] = 'normal'
        self.addToPreferencesBtn['state'] = 'normal'


        
class PreferenceListDisplay(ttk.Frame):
    """Displays the preference statements for the selected DM."""
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master)

        self.game = game
        self.label = ttk.Label(self,text="Preferences")
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
        self.rowconfigure(1,weight=1)

        self.disp.heading('state', text='Preferred Condition')
        self.disp.heading('weight', text='Weighting')
        self.disp['show'] = 'headings'

        self.label.grid(column=0,row=0,columnspan=5,sticky=(N,S,E,W))
        
        self.disp.grid(column=0,row=1,columnspan=5,sticky=(N,S,E,W))
        self.scrl.grid(column=5,row=1,sticky=(N,S,E,W))
        self.disp.configure(yscrollcommand=self.scrl.set)

        self.upBtn.grid(column=2,row=3,sticky=(N,S,E,W))
        self.downBtn.grid(column=3,row=3,sticky=(N,S,E,W))
        self.delBtn.grid(column=4,row=3,sticky=(N,S,E,W))

        self.disp.bind('<<TreeviewSelect>>', self.selChgCmd)

    def refresh(self):
        """Fully refreshes the list displayed"""
        for child in self.disp.get_children():
            self.disp.delete(child)
        if self.dm is not None:
            self.dm.weightPreferences()
            self.keys = []
            for pref in self.dm.preferences:
                key = self.disp.insert('','end',text=pref.name)
                self.disp.set(key,'state',pref.name)
                self.disp.set(key,'weight',pref.weight)
                self.keys.append(key)
        
        
    def disable(self,event=None):
        self.disp['selectmode'] = 'none'
        self.upBtn['state'] = 'disabled'
        self.downBtn['state'] = 'disabled'
        self.delBtn['state'] = 'disabled'
    
    def enable(self,event=None):
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
        self.event_generate('<<SelPref>>',x=self.selIdx)

    def upCmd(self,*args):
        """Called whenever an item is moved upwards."""
        idx = self.selIdx
        if (idx !=0) and (self.dm is not None):
            newIdx = idx-1
            self.dm.preferences.moveCondition(idx,idx-1)
            self.event_generate('<<ValueChange>>')
            self.disp.selection_set(self.keys[newIdx])
            self.selChgCmd()

    def downCmd(self,*args):
        """Called whenever an item is moved downwards."""
        idx = self.selIdx
        if (idx != len(self.dm.preferences)-1) and (self.dm is not None):
            newIdx = idx+1
            self.dm.preferences.moveCondition(idx,idx+1)
            self.event_generate('<<ValueChange>>')
            self.disp.selection_set(self.keys[newIdx])
            self.selChgCmd()

    def delCmd(self,*args):
        """Called when an item is deleted."""
        if self.selIdx < len(self.keys)-1:
            newSelIdx = self.selIdx
        elif len(self.keys) <= 1:
            newSelIdx = None
        else:
            newSelIdx = self.selIdx-1
                
        self.dm.preferences.removeCondition(self.selIdx)
        self.event_generate('<<ValueChange>>')
        
        if newSelIdx is not None:
            self.disp.selection_set(self.keys[newSelIdx])
        else:
            self.selId = None
            self.selIdx = None
