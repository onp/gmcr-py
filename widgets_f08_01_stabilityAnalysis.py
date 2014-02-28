# Copyright:   (c) Oskar Petersons 2013

"""Compound widgets for Stability Analysis screen.

Loaded by the frame_08_stabilityAnalysis module.
"""

from tkinter import *
from tkinter import ttk
from data_02_conflictSolvers import InverseSolver

class StatusQuoAndGoals(ttk.Frame):
    def __init__(self,master,conflict):
        ttk.Frame.__init__(self,master)
        
        self.conflict = conflict
        
        self.statusQuoVar = StringVar()
        self.goalVars = []
        self.removeCommands = []
        self.cleanRow = 2
        
        self.listFrame = ttk.Frame(self)
        self.listFrame.grid(row=0,column=0,sticky=(N,S,E,W))

        self.statusQuoLabel = ttk.Label(self.listFrame,text="Status Quo:")
        self.statusQuoLabel.grid(row=0,column=0,columnspan=2,sticky=(N,S,E,W))
        self.statusQuoSelector = ttk.Combobox(self.listFrame,textvariable=self.statusQuoVar,state='readonly')
        self.statusQuoSelector.grid(row=0,column=2,sticky=(N,S,E,W))
        ttk.Separator(self.listFrame,orient=HORIZONTAL).grid(row=1,column=0,columnspan=3,sticky=(N,S,E,W))
        
        self.addGoalButton = ttk.Button(self,text="Add Goal",command = self.addGoal)
        self.addGoalButton.grid(row=1,column=0,sticky=(N,S,E,W))
        
        self.refresh()
        
    def refresh(self):
        self.statusQuoSelector['values'] = tuple(self.conflict.feasibles.ordered)
        self.statusQuoSelector.current(0)
        for rmv in self.removeCommands:
            rmv()
        self.cleanRow = 2
        
    def addGoal(self,event=None):
        goalVar = StringVar()
        
        rmvBtn = ttk.Button(self.listFrame,text="X",width=5)
        label = ttk.Label(self.listFrame,text="Goal:")
        selector = ttk.Combobox(self.listFrame,textvariable=goalVar,state='readonly')
        selector['values'] = tuple(self.conflict.feasibles.ordered)
        
        def removeGoal(event=None):
            label.destroy()
            selector.destroy()
            rmvBtn.destroy()
            self.removeCommands.remove(removeGoal)
            self.goalVars.remove(goalVar)
            
        rmvBtn.configure(command=removeGoal)
        self.removeCommands.append(removeGoal)
        self.goalVars.append(goalVar)
        
        rmvBtn.grid(row=self.cleanRow,column=0,sticky=(N,S,E,W))
        label.grid(row=self.cleanRow,column=1,sticky=(N,S,E,W))
        selector.grid(row=self.cleanRow,column=2,sticky=(N,S,E,W))
        self.cleanRow += 1
        
class reachableTreeViewer(ttk.Frame):
    def __init__(self,master,conflict):
        ttk.Frame.__init__(self,master)
        
        self.conflict = conflict
        
        
        
        