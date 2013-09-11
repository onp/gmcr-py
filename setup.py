from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

executables = [
    Executable('a_Main_Window.py', base='Win32GUI', targetName = 'gmcr')
]

setup(name='gmcr-py',
      version = '0.1',
      description = 'Graph Model for Conflict Resolution',
      options = dict(build_exe = buildOptions),
      executables = executables)
