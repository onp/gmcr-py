from tkinter import *
from tkinter import ttk
import data_03_gmcrUtilities as gmcrUtil

class PreferenceVectorEditor(ttk.Frame):
    """Displays the preference vector for a single Decision Maker and allows it to be edited."""
    def __init__(self,master,game,dm):
        ttk.Frame.__init__(self,master,borderwidth=2)
        
        self.master = master
        self.game = game
        self.dm = dm
        
        self.columnconfigure(1,weight=1)
        
        self.dmText = StringVar(value = dm.name + ': ')
        self.dmLabel = ttk.Label(self,textvariable=self.dmText,width=20)
        self.dmLabel.grid(row=0,column=0,sticky=(N,S,E,W))
        
        self.prefVecVar = StringVar(value=str(dm.preferenceVector))
        self.prefVecEntry = ttk.Entry(self,textvariable=self.prefVecVar)
        self.prefVecEntry.grid(row=0,column=1,sticky=(N,S,E,W))
        
        self.errorDetails = None
        
        self.prefVecEntry.bind("<FocusOut>",self.onFocusOut)
        
    def onFocusOut(self,event):
        print('focused out')
        prefVec = eval(self.prefVecVar.get())
        self.errorDetails = gmcrUtil.validatePreferenceVector(prefVec,self.game.feasibles)
        if self.errorDetails:
            self.errorDetails += "  See DM %s's preference vector."%(self.dm.name)
            self.master.event_generate("<<errorChange>>")
            return
        print('passed test')
        self.dm.preferenceVector = prefVec
        gmcrUtil.mapPrefVec2Payoffs(self.dm,self.game.feasibles)
        
        
class PVecEditMaster(ttk.Frame):
    """Contains a PreferenceVectorEditor for each DM, plus an error box."""
        
    def __init__(self,master,game):
        ttk.Frame.__init__(self,master,borderwidth=2)
        
        self.game = game
        
        self.columnconfigure(0,weight=1)
        
        self.activateButton = ttk.Button(self,
                text="Press to enable manual preference vector changes",
                command=self.enableEditing)
        self.activateButton.grid(row=0,column=0,sticky=(N,S,E,W))
        
        self.editorFrame = ttk.Frame(self)
        self.editorFrame.grid(row=1,column=0,sticky=(N,S,E,W))
        
        self.errorDisplay = Text(self,height=6)
        self.errorDisplay['state'] = 'disabled'
        self.errorDisplay.grid(row=2,column=0,sticky=(N,E,W))
        
        self.bind('<<errorChange>>',self.updateErrors)
        
        
    def refresh(self):
        for child in self.editorFrame.winfo_children():
            child.destroy()
            
        self.vectorEditors = []
        
        for idx,dm in enumerate(self.game.decisionMakers):
            newEditor = PreferenceVectorEditor(self,self.game,dm)
            self.vectorEditors.append(newEditor)
            newEditor.grid(row=idx,column=0,sticky=(N,S,E,W))
            
        self.errorDisplay['state'] = 'normal'
        self.errorDisplay.delete('1.0','end')
        self.errorDisplay['state'] = 'disabled'
           
    def enableEditing(self,event):
        pass

    def updateErrors(self,event):
        messages = [editor.errorDetails for editor in self.vectorEditors if editor.errorDetails]
        text = '\n'.join(messages)
        self.errorDisplay['state'] = 'normal'
        self.errorDisplay.delete('1.0','end')
        self.errorDisplay.insert('1.0',text)
        self.errorDisplay['state'] = 'disabled'



