"""Script for generation of an .msi install package for GMCR-py.

Call from console with `python setup.py bdist_msi`

Built versions will appear in the `dist` top directory.
"""

# Copyright:   (c) Oskar Petersons 2013

from cx_Freeze import setup, Executable

# Set other directories to be included.
buildOptions = {'include_files': 
                    ['save_files/','icons/','gmcr-vis/css/','gmcr-vis/js/','gmcr-vis/js-lib/','gmcr-vis/json/','gmcr-vis/favicon.ico','gmcr-vis/index.html'],
                'silent': True}

# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "gmcr-py",                # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]gmcr.exe",    # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     ),
    ("StartMenuShortcut",      # Shortcut
     "ProgramMenuFolder",      # Directory_
     "gmcr-py",                # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]gmcr.exe",    # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]

# Create the table dictionary
msi_data = {"Shortcut": shortcut_table}

# Change some default MSI options and specify the use of the above defined tables
bdist_msi_options = {'data': msi_data,
                     'upgrade_code':'272b3c8b-515d-4e8d-980c-f007dac5ecdf'}

# Specify executables
executables = [
    Executable('a_Main_Window.py',
                base='Win32GUI',
                targetName = 'gmcr.exe',
                appendScriptToExe=True,
                appendScriptToLibrary=False,
                icon='gmcr.ico',
                shortcutName='gmcr-py',
                shortcutDir='ProgramMenuFolder')
]

# Run setup
setup(name='gmcr-py',
      version = '0.3',
      description = 'Graph Model for Conflict Resolution',
      options = {'build_exe': buildOptions,
                 'bdist_msi': bdist_msi_options},
      executables = executables)