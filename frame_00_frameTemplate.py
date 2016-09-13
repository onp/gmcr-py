# Copyright:   (c) Oskar Petersons 2013

"""Base class for frames to be loaded into the main window."""

from tkinter import Frame, PhotoImage, StringVar, N, S, E, W
from tkinter import ttk

tkNSEW = (N, S, E, W)


class FrameTemplate(Frame):
    """Base class for frames to be loaded into the main window."""

# ########################     INITIALIZATION  ################################
    def __init__(self, master, conflict, buttonLabel, activeIcon,
                 inactiveIcon, helpText):
        """Initialize the Frame. Does not build widgets."""
        ttk.Frame.__init__(self, master)

        self.infoFrame = ttk.Frame(master, relief='sunken', borderwidth='3')
        self.helpFrame = ttk.Frame(master, relief='sunken', borderwidth='3')

        # Connect to active conflict module
        self.conflict = conflict

        # Label used for button to select frame in the main program.
        self.buttonLabel = buttonLabel
        # Image used on button to select frame, when frame is active.
        self.activeIcon = PhotoImage(file=activeIcon)
        # Image used on button to select frame, when frame is inactive.
        self.inactiveIcon = PhotoImage(file=inactiveIcon)
        # Help text string variable.
        self.helpVar = StringVar(value=self.helpText)

        self.built = False
        self.button = None

    def makeButton(self, buttonMaster, mainWindow):
        """Create a button to be used ot enter the frame."""
        def onClick(*args):
            print('Loading {} frame...'.format(self.buttonLabel))
            mainWindow.frameLeave()
            self.enter()
            mainWindow.contentFrame.currFrame = self

        mainWindow.frameBtnCmds.append(onClick)

        self.button = ttk.Button(buttonMaster, text=self.buttonLabel,
                                 image=self.inactiveIcon, compound="top",
                                 width=20, command=lambda: onClick())
        self.button.grid(column=len(mainWindow.frameBtnList), row=0,
                         sticky=tkNSEW)
        return self.button

    def hasRequiredData(self):
        """Check that minimum data for input of misperceivedStates exists.

        Always returns True. Should be re-implmented in subclass if an actual
        test is needed.
        """
        return True

    def dataChanged(self):
        """Check if data has changed since the last build of the Frame.

        Always returns False. Should be re-implmented in subclass if an actual
        test is needed.
        """
        return False

    def clearFrame(self):
        """Destroy all child widgets and mark frame as unbuilt."""
        self.built = False
        for child in self.winfo_children():
            child.destroy()
        self.infoFrame.grid_forget()
        self.helpFrame.grid_forget()

    def enter(self):
        """Re-grid the screen into the master. Perform required updates."""
        if not self.built:
            self.buildFrame()
        self.refreshWidgets()
        self.grid()
        self.infoFrame.grid()
        self.helpFrame.grid()
        if self.button:
            self.button['image'] = self.activeIcon

    def leave(self):
        """Un-grid the screen. Perform exit update tasks."""
        self.grid_remove()
        self.infoFrame.grid_remove()
        self.helpFrame.grid_remove()
        if self.button:
            self.button['image'] = self.inactiveIcon
