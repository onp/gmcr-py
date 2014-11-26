# Copyright:   (c) Oskar Petersons 2013

"""Compound widgets for Stability Analysis screen.

Loaded by the frame_08_stabilityAnalysis module.
"""

from tkinter import *
from tkinter import ttk

class StatusQuoAndGoals(ttk.Frame):
    def __init__(self,master,conflict):
        ttk.Frame.__init__(self,master)
        
        self.conflict = conflict
        
        self.statusQuoVar = StringVar()
        self.goalGetters = []
        self.removeCommands = []
        self.cleanRow = 2
        
        self.listFrame = ttk.Frame(self)
        self.listFrame.grid(row=0,column=0,sticky=(N,S,E,W))
        self.listFrame.columnconfigure(2,weight=1)
        self.columnconfigure(0,weight=1)

        self.statusQuoLabel = ttk.Label(self.listFrame,text="Status Quo:")
        self.statusQuoLabel.grid(row=0,column=0,columnspan=2,sticky=(N,S,E,W))
        self.statusQuoSelector = ttk.Combobox(self.listFrame,textvariable=self.statusQuoVar,state='readonly')
        self.statusQuoSelector.grid(row=0,column=2,columnspan=2,sticky=(N,S,E,W))
        ttk.Separator(self.listFrame,orient=HORIZONTAL).grid(row=1,column=0,columnspan=3,sticky=(N,S,E,W))
        
        self.addGoalButton = ttk.Button(self,text="Add Goal",command = self.addGoal)
        self.addGoalButton.grid(row=1,column=0,sticky=(N,S,E,W))
        
        self.statusQuoSelector.bind('<<ComboboxSelected>>',self.sqChange)
        self.refresh()
        
    def refresh(self):
        self.statusQuoSelector['values'] = tuple(self.conflict.feasibles.ordered)
        self.statusQuoSelector.current(0)
        for rmv in self.removeCommands:
            rmv()
        self.cleanRow = 2
        
    def addGoal(self,event=None):
        goalVar = StringVar()
        stabilityVar = StringVar()
        
        rmvBtn = ttk.Button(self.listFrame,text="X",width=5)
        label = ttk.Label(self.listFrame,text="Goal:")
        stateSelector = ttk.Combobox(self.listFrame,textvariable=goalVar,state='readonly',width=5)
        stateSelector['values'] = tuple(self.conflict.feasibles.ordered)
        desiredStable = ttk.Combobox(self.listFrame,textvariable=stabilityVar,state='readonly',width=10)
        desiredStable['values'] = tuple(['Stable','Unstable'])
        
        def getGoal():
            return [stateSelector.current(), desiredStable.current()==0]
        
        def removeGoal(event=None):
            self.removeCommands.remove(removeGoal)
            self.goalGetters.remove(getGoal)
            label.destroy()
            stateSelector.destroy()
            desiredStable.destroy()
            rmvBtn.destroy()
            self.goalChange()
            
            
        rmvBtn.configure(command=removeGoal)
        self.removeCommands.append(removeGoal)
        self.goalGetters.append(getGoal)
        
        stateSelector.bind("<<ComboboxSelected>>",self.goalChange)
        desiredStable.bind("<<ComboboxSelected>>",self.goalChange)
        
        rmvBtn.grid(row=self.cleanRow,column=0,sticky=(N,S,E,W))
        label.grid(row=self.cleanRow,column=1,sticky=(N,S,E,W))
        stateSelector.grid(row=self.cleanRow,column=2,sticky=(N,S,E,W))
        desiredStable.grid(row=self.cleanRow,column=3,sticky=(N,S,E,W))
        desiredStable.current(1)
        self.cleanRow += 1
        
    def sqChange(self,event=None):
        self.event_generate("<<StatusQuoChanged>>")
        
    def goalChange(self,event=None):
        self.event_generate("<<GoalChanged>>")
        
    def getGoals(self,event=None):
        goals = []
        for gt in self.goalGetters:
            goals.append(gt())
        return goals
        
class ReachableTreeViewer(ttk.Frame):
    def __init__(self,master,conflict,solOwner):
        ttk.Frame.__init__(self,master)
        
        self.conflict = conflict
        self.owner = solOwner
        self.found = []
        self.notFound = []
        self.foundUI = []
        self.notFoundUI = []
        self.statusQuo = None
        
        self.reachableTree = ttk.Treeview(self,selectmode='browse')
        self.reachableTree.grid(row=0,column=0,sticky=(N,S,E,W))
        self.scrollX = ttk.Scrollbar(self, orient=HORIZONTAL,command = self.reachableTree.xview)
        self.scrollX.grid(row=1,column=0,sticky=(N,S,E,W))
        self.scrollY = ttk.Scrollbar(self, orient=VERTICAL,command = self.reachableTree.yview)
        self.scrollY.grid(row=0,column=1,sticky=(N,S,E,W))
        self.reachableTree.configure(xscrollcommand=self.scrollX.set)
        self.reachableTree.configure(yscrollcommand=self.scrollY.set)
        
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        
        self.reachableTree.column("#0",stretch=True,minwidth=100,width=120)
        self.reachableTree.heading("#0",text="State Number")
        
        columnNames = ("DM","YN","Decimal","Payoff","UI")
        self.reachableTree.configure(columns=columnNames)
        
        for col in columnNames:
            self.reachableTree.column(col,stretch=True,minwidth=60,width=80,anchor="center")
            self.reachableTree.heading(col,text=col)
        
        self.reachableTree.tag_configure("Y",background="green")
        self.buildTree(0,watchFor=[])
        
    def buildTree(self,statusQuo,depth=5,lastDM=None,parent="",wasUI="N",onUIpath=True,watchFor=None):
        sol = self.owner.sol
        if lastDM is None:
            self.statusQuo = statusQuo
            self.notFound = list(set(watchFor))
            self.found = []
            self.notFoundUI = list(set(watchFor))
            self.foundUI = []
            for child in self.reachableTree.get_children():
                self.reachableTree.delete(child)
            newNode = self.reachableTree.insert(parent,'end',text=str(statusQuo+1))
        else:
            vals = (lastDM.name,
                    self.conflict.feasibles.yn[statusQuo],
                    self.conflict.feasibles.decimal[statusQuo],
                    lastDM.payoffs[statusQuo],
                    wasUI)
            newNode = self.reachableTree.insert(parent,'end',text=str(statusQuo+1),values=vals,tags=(wasUI,))
            
        if statusQuo in self.notFound:
            self.notFound.remove(statusQuo)
            self.found.append(statusQuo)
        if onUIpath:
            if statusQuo in self.notFoundUI:
                self.notFoundUI.remove(statusQuo)
                self.foundUI.append(statusQuo)
        
        if depth>0:
            for co in [dm for dm in sol.conflict.coalitions if dm is not lastDM]:
                for reachable in sol.reachable(co,statusQuo):
                    ui = "Y" if co.payoffMatrix[statusQuo,reachable]>0 else "N"
                    uiPath = onUIpath and (ui=="Y")
                    self.buildTree(reachable,depth-1,co,newNode,ui,uiPath)
                    
    def goalInfo(self,event=None):
        message = ""
        if len(self.found)>0:
            message += "Goal states " +str([x+1 for x in self.found])[1:-1] + " are reachable from %s.\n"%(self.statusQuo+1)
        if len(self.notFound)>0:
            message += "States " +str([x+1 for x in self.notFound])[1:-1] + " are NOT reachable from %s.\n"%(self.statusQuo+1)
        if message != "":
            message += "\n"
        if len(self.foundUI)>0:
            message += "Goal states " +str([x+1 for x in self.foundUI])[1:-1] + " are reachable from %s solely by UIs.\n"%(self.statusQuo+1)
        if len(self.notFoundUI)>0:
            message += "States " +str([x+1 for x in self.notFoundUI])[1:-1] + " are NOT reachable from %s solely by UIs.\n"%(self.statusQuo+1)
        message += "\n"
        return message
                
            
class PatternNarrator(ttk.Frame):
    def __init__(self,master,conflict,solOwner):
        ttk.Frame.__init__(self,master)
        
        self.conflict = conflict
        self.owner = solOwner
        
        self.label = ttk.Label(self,text="Requirements for goals to be met:")
        self.label.grid(row=0,column=0,sticky=(N,S,E,W))
        
        self.textBox = Text(self,wrap="word")
        self.textBox.grid(row=1,column=0,sticky=(N,S,E,W))
        self.scrollY = ttk.Scrollbar(self,orient=VERTICAL,command=self.textBox.yview)
        self.textBox.configure(yscrollcommand=self.scrollY.set)
        self.scrollY.grid(row=1,column=1,sticky=(N,S,E,W))
        
        self.rowconfigure(1,weight=1)
        self.columnconfigure(0,weight=1)
        
        self.updateNarration()
        
    def updateNarration(self,event=None,goalInfo=""):
        message = goalInfo
        if not self.owner.sol.validGoals():
            message += "No valid goals set."
        else:
            message += "\n" + self.owner.sol.nash().asString()
            message += "\n" + self.owner.sol.seq().asString()
            
        self.textBox.delete('1.0','end')
        self.textBox.insert('1.0',message)
        
        
        