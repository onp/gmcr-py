# Copyright:   (c) Oskar Petersons 2013

"""Widgets used for validating and manually entering state rankings.

Loaded by the frame_05_preferenceRanking module.
"""

from tkinter import StringVar, N, S, E, W, Text
from tkinter import ttk
import data_03_gmcrUtilities as gmcrUtil

NSEW = (N, S, E, W)


class RankingEditor(ttk.Frame):
    """Display and edit the state ranking for a single Decision Maker."""

    def __init__(self, master, conflict, dm):
        """Initialize a RankingEditor widget for a decision maker."""
        ttk.Frame.__init__(self, master, borderwidth=2)

        self.master = master
        self.conflict = conflict
        self.dm = dm

        self.columnconfigure(1, weight=1)

        self.dmText = StringVar(value=dm.name + ': ')
        self.dmLabel = ttk.Label(self, textvariable=self.dmText, width=20)
        self.dmLabel.grid(row=0, column=0, sticky=NSEW)

        self.prefRankVar = StringVar(value=str(dm.preferenceRanking))
        self.prefRankEntry = ttk.Entry(self, textvariable=self.prefRankVar)
        self.prefRankEntry.grid(row=0, column=1, sticky=NSEW)

        self.errorDetails = None

        self.prefRankEntry.bind("<FocusOut>", self.onFocusOut)

    def onFocusOut(self, event):
        """Validate the preference ranking when focus leaves the widget."""
        try:
            prefRank = eval(self.prefRankVar.get())
        except SyntaxError:
            self.errorDetails = ("DM {}'s preference ranking is "
                                 "invalid.").format(self.dm.name)
            self.master.event_generate("<<errorChange>>")
            return
        except NameError:
            self.errorDetails = ("DM {}'s preference ranking is "
                                 "invalid.").format(self.dm.name)
            self.master.event_generate("<<errorChange>>")
            return
        self.errorDetails = gmcrUtil.validatePreferenceRanking(
            prefRank, self.conflict.feasibles)
        if self.errorDetails:
            self.errorDetails += ("  Check DM {}'s preference "
                                  "ranking.").format(self.dm.name)
            self.master.event_generate("<<errorChange>>")
            return
        self.dm.preferenceRanking = prefRank
        self.dm.calculatePreferences()
        self.master.event_generate("<<errorChange>>")

    def enableWidget(self):
        """Enable editting of the ranking."""
        self.prefRankEntry['state'] = 'normal'

    def disableWidget(self):
        """Disable editting of the ranking."""
        self.prefRankEntry['state'] = 'disabled'


class PRankEditMaster(ttk.Frame):
    """Contains a RankingEditor for each DM, plus an error box."""

    def __init__(self, master, conflict):
        """Initialize a preference ranking master widget for the conflict."""
        ttk.Frame.__init__(self, master, borderwidth=2)

        self.conflict = conflict

        self.columnconfigure(0, weight=1)

        self.activateButton = ttk.Button(
            self,
            text="Press to enable manual preference ranking changes",
            command=self.enableEditing)
        self.activateButton.grid(row=0, column=0, sticky=NSEW)

        self.editorFrame = ttk.Frame(self)
        self.editorFrame.grid(row=2, column=0, sticky=NSEW)
        self.editorFrame.columnconfigure(0, weight=1)

        self.errorDisplay = Text(self, height=6)
        self.errorDisplay['state'] = 'disabled'
        self.errorDisplay.grid(row=3, column=0, sticky=(N, E, W))

        self.editorFrame.bind('<<errorChange>>', self.updateErrors)

    def refresh(self):
        """Refresh the widget and all children."""
        for child in self.editorFrame.winfo_children():
            child.destroy()

        self.rankingEditors = []

        for idx, dm in enumerate(self.conflict.decisionMakers):
            newEditor = RankingEditor(self.editorFrame, self.conflict, dm)
            self.rankingEditors.append(newEditor)
            newEditor.grid(row=idx, column=0, sticky=NSEW)

        self.updateErrors()

        if not self.conflict.useManualPreferenceRanking:
            self.activateButton['text'] = ("Click to enable manual preference "
                                           "ranking changes")
            self.activateButton['state'] = 'normal'
            for editor in self.rankingEditors:
                editor.disableWidget()
        else:
            self.activateButton['text'] = ("Preference rankings entered below "
                                           "will be used in analysis.")
            self.activateButton['state'] = 'disabled'

    def enableEditing(self):
        """Switch on manual editing of the preference rankings."""
        self.activateButton['text'] = ("Preference rankings entered below "
                                       "will be used in analysis.")
        self.activateButton['state'] = 'disabled'
        for editor in self.rankingEditors:
            editor.enableWidget()
        self.conflict.useManualPreferenceRanking = True

    def updateErrors(self, event=None):
        """Update the messages in the error box."""
        messages = [editor.errorDetails for editor in self.rankingEditors
                    if editor.errorDetails]
        self.conflict.preferenceErrors = len(messages)

        self.errorDisplay['state'] = 'normal'
        self.errorDisplay.delete('1.0', 'end')
        if len(messages) > 0:
            text = '\n'.join(messages)
            self.errorDisplay.insert('1.0', text)
            self.errorDisplay['foreground'] = 'red'
        else:
            self.errorDisplay.insert(
                '1.0', "No Errors. Preference rankings are valid.")
            self.errorDisplay['foreground'] = 'black'
            self.event_generate("<<PreferenceRankingChange>>")
        self.errorDisplay['state'] = 'disabled'
