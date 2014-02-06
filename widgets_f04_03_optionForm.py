# Copyright:   (c) Oskar Petersons 2013

"""Various widgets used in editing and displaying prioritization-based preferences.

Loaded by the frame_04_preferencePrioritization module.
"""

from tkinter import *
from tkinter import ttk
import numpy

class OptionFormTable(ttk.Frame):
    def __init__(self,master,conflict):
        ttk.Frame.__init__(self,master)
        
        self.conflict = conflict
        
        #widgets
        self.table = ttk.Treeview(self)
        self.scrollY = ttk.Scrollbar(self, orient=VERTICAL,command = self.table.yview)
        self.scrollX = ttk.Scrollbar(self, orient=HORIZONTAL,command = self.table.xview)
        
        #configuration
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        
        self.table['show'] = 'headings'
        self.table.grid(column=0,row=0,sticky=(N,S,E,W))
        self.scrollY.grid(column=1,row=0,sticky=(N,S,E,W))
        self.scrollX.grid(column=0,row=1,sticky=(N,S,E,W))
        self.table.configure(yscrollcommand=self.scrollY.set)
        self.table.configure(xscrollcommand=self.scrollX.set)
        
        self.buildTable()
    
    def buildTable(self,focusDM=None):
        if focusDM is not None:
            rowCount = len(self.conflict.options)+3
        else:
            rowCount = len(self.conflict.options)+len(self.conflict.decisionMakers)+2
        
        columnCount = len(self.conflict.feasibles)+2
        tableData = numpy.zeros((rowCount,columnCount),dtype="<U20")
        
        #labels
        tableData[0,1] = "Ordered"
        tableData[1,1] = "Decimal"
        
        ##DMs and options
        currRow = 2
        for dm in self.conflict.decisionMakers:
            tableData[currRow,0] = dm.name
            for opt in dm.options:
                tableData[currRow,1] = opt.name
                currRow += 1
                
        ##payoff labels
        if focusDM is None:
            for dm in self.conflict.decisionMakers:
                tableData[currRow,0:2] = ["Payoff For:",dm.name]
                currRow += 1
        else:
            tableData[currRow,0:2] = ["Payoff For:",focusDM.name]
                
        #fill states
        currCol = 2
        feasibles = self.conflict.feasibles
        for state in range(len(feasibles)):
            newCol = [feasibles.ordered[state],feasibles.decimal[state]]+list(feasibles.yn[state])
            if focusDM is None:
                for dm in self.conflict.decisionMakers:
                    newCol.append(dm.payoffs[state])
            else:
                newCol.append(focusDM.payoffs[state])
            tableData[:,currCol] = newCol
            currCol += 1
            
        #sort
        if focusDM is not None:
            tableData[:,2:] = tableData[:,2:][:,tableData[-1,2:].argsort()[::-1]]
        
        #push to display
        
        for child in self.table.get_children():
            self.table.delete(child)
        
        self.table['columns'] = list(range(len(feasibles) + 2))
        
        for row in range(tableData.shape[0]):
            if row<2:
                tag = "head"
            elif row<(len(self.conflict.options)+2):
                tag = "body"
            else:
                tag = "foot"
            self.table.insert('','end',values = tableData[row,:].tolist(),tags = (tag,))
            
        self.table.tag_configure("head",background="green")
        self.table.tag_configure("foot",background="green")
        
        #column sizing
        for col in range(len(feasibles) + 2):
            self.table.column(col,stretch=False)
        self.table.column(0,width=200)
        self.table.column(0,minwidth=150)
        self.table.column(1,width=200)
        self.table.column(1,minwidth=150)
        for col in range(2,(len(feasibles) + 2)):
            self.table.column(col,width=22)
            self.table.column(col,minwidth=17)