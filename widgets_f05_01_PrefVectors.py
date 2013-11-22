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
        prefVec = eval(self.prefVecVar.get())
        self.errorDetails = gmcrUtil.validatePreferenceVector(prefVec,self.game.feasibles)
        if self.errorDetails:
            self.errorDetails += "  See DM %s's preference vector."%(self.dm.name)
            self.master.event_generate("<<errorChange>>")
            return
        print('passed test')
        self.master.event_generate("<<errorChange>>")
        self.dm.preferenceVector = prefVec
        self.dm.calculatePreferences()
        
    def enableWidget(self):
        self.prefVecEntry['state'] = 'normal'
        
    def disableWidget(self):
        self.prefVecEntry['state'] = 'disabled'
        
        
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
        self.editorFrame.grid(row=2,column=0,sticky=(N,S,E,W))
        self.editorFrame.columnconfigure(0,weight=1)
        
        self.errorDisplay = Text(self,height=6)
        self.errorDisplay['state'] = 'disabled'
        self.errorDisplay.grid(row=3,column=0,sticky=(N,E,W))
        
        self.editorFrame.bind('<<errorChange>>',self.updateErrors)


    def refresh(self):
        for child in self.editorFrame.winfo_children():
            child.destroy()

        self.vectorEditors = []

        for idx,dm in enumerate(self.game.decisionMakers):
            newEditor = PreferenceVectorEditor(self.editorFrame,self.game,dm)
            self.vectorEditors.append(newEditor)
            newEditor.grid(row=idx,column=0,sticky=(N,S,E,W))
        
        self.updateErrors()
        
        if not self.game.useManualPreferenceVectors:
            self.activateButton['text'] = "Press to enable manual preference vector changes"
            self.activateButton['state'] = 'normal'
            for editor in self.vectorEditors:
                editor.disableWidget()
        else:
            self.activateButton['text'] = "Preference Vectors entered below will be used in analysis."
            self.activateButton['state'] = 'disabled'

    def enableEditing(self):
        """Switches on manual editing of the preference vectors."""
        self.activateButton['text'] = "Preference Vectors entered below will be used in analysis."
        self.activateButton['state'] = 'disabled'
        for editor in self.vectorEditors:
            editor.enableWidget()
        self.game.useManualPreferenceVectors = True

    def updateErrors(self,event=None):
        messages = [editor.errorDetails for editor in self.vectorEditors if editor.errorDetails]
        self.game.preferenceErrors = len(messages)
        self.event_generate("<<breakingChange>>")

        self.errorDisplay['state'] = 'normal'
        self.errorDisplay.delete('1.0','end')
        if len(messages)>0:
            text = '\n'.join(messages)
            self.errorDisplay.insert('1.0',text)
            self.errorDisplay['foreground'] = 'red'
        else:
            self.errorDisplay.insert('1.0',"No Errors.  Preference vectors are valid.")
            self.errorDisplay['foreground'] = 'black'
        self.errorDisplay['state'] = 'disabled'

