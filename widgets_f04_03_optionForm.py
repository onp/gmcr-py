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
        self.tableCanvas = Canvas(self)
        self.table = ttk.Frame(self.tableCanvas)
        self.scrollY = ttk.Scrollbar(self, orient=VERTICAL,command = self.tableCanvas.yview)
        self.scrollX = ttk.Scrollbar(self, orient=HORIZONTAL,command = self.tableCanvas.xview)
        
        #configuration
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        
        def resize(event):
            self.tableCanvas.configure(scrollregion=self.tableCanvas.bbox("all"))
        
        self.tableCanvas.grid(column=0,row=0,sticky=(N,S,E,W))
        self.scrollY.grid(column=1,row=0,sticky=(N,S,E,W))
        self.scrollX.grid(column=0,row=1,sticky=(N,S,E,W))
        self.tableCanvas.configure(yscrollcommand=self.scrollY.set)
        self.tableCanvas.configure(xscrollcommand=self.scrollX.set)
        self.tableCanvas.create_window((0,0),window=self.table,anchor='nw')
        self.table.bind("<Configure>",resize)
        
        self.style = ttk.Style()
        # styles for cells in the Option form table. CHANGE COLOURS HERE.
        self.style.configure('states.TLabel',background="grey80")
        self.style.configure('yn.TLabel',background="white")
        self.style.configure('payoffs.TLabel',background="grey80")
        self.style.configure('hover.TLabel',background="lightpink")
        
        self.buildTable()
    
    def buildTable(self,focusDM=None):
        if len(self.conflict.feasibles)>1000:
            note = ttk.Label(self.table,text="More than 1000 states. No table will be drawn")
            note.grid(row=1,column=1,sticky=(N,S,E,W))
            return
            
            
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
            sortOrder = tableData[-1,2:].astype('int').argsort()[::-1]
            tableData[:,2:] = tableData[:,2:][:,sortOrder]
        
        #push to display
        
        for child in self.table.winfo_children():
            child.destroy()
            
        rows = [[] for row in range(tableData.shape[0])]
        columns = [[] for col in range(tableData.shape[1])]
        
        for row in range(tableData.shape[0]):
            if row<2:
                tag = "states"
            elif row<(len(self.conflict.options)+2):
                tag = "yn"
            else:
                tag = "payoffs"
            for col in range(tableData.shape[1]):
                if col <2:
                    newEntry = ttk.Label(self.table,text=tableData[row,col],style=tag+".TLabel")
                else:
                    newEntry = ttk.Label(self.table,text=tableData[row,col],style=tag+".TLabel",width=4)

                newEntry.grid(row=row,column=col,sticky=(N,S,E,W))
                    
                def enterCell(event=None,row=row,col=col):
                    for cell,tag in rows[row]:
                        cell.configure(style="hover.TLabel")
                    for cell,tag in columns[col]:
                        cell.configure(style="hover.TLabel")
                
                def exitCell(event=None,row=row,col=col):
                    for cell,tag in rows[row]:
                        cell.configure(style=tag+".TLabel")
                    for cell,tag in columns[col]:
                        cell.configure(style=tag+".TLabel")
                
                if (row < 2) and (col >=2):
                    columns[col].append([newEntry,tag])
                    newEntry.bind("<Enter>", enterCell)
                    newEntry.bind("<Leave>", exitCell)
                elif (row >= 2) and (col == 1):
                    rows[row].append([newEntry,tag])
                    newEntry.bind("<Enter>", enterCell)
                    newEntry.bind("<Leave>", exitCell)
                elif (col >= 2) and (row >= 2):
                    rows[row].append([newEntry,tag])
                    columns[col].append([newEntry,tag])
                    newEntry.bind("<Enter>", enterCell)
                    newEntry.bind("<Leave>", exitCell)
                