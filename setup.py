from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = {'include_files': ['save_files/','icons/']}

executables = [
    Executable('a_Main_Window.py', base='Win32GUI',
                targetName = 'gmcr.exe',appendScriptToExe=True,
                appendScriptToLibrary=False,
                icon='gmcr.ico')
]

setup(name='gmcr-py',
      version = '0.1',
      description = 'Graph Model for Conflict Resolution',
      options = {   'build_exe': buildOptions},
      executables = executables)