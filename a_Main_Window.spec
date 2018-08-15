# -*- mode: python -*-

block_cipher = None


a = Analysis(['a_Main_Window.py'],
             pathex=['C:\\Users\\oskar\\Documents\\GitHub\\gmcr-py'],
             binaries=[],
             datas=[('Examples', 'Examples'),
                    ('icons', 'icons'),
                    ('gmcr-vis', 'gmcr-vis'),
                    ('gmcr.ico', '.'),
                    ('GMCR+handout.pdf', '.'),
                    ('END USER AGREEMENT.txt', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='GMCRplus',
          debug=False,
          strip=False,
          upx=True,
          console=True,
          icon='gmcr.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='GMCRplus_v0.3.15')
