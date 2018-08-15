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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='GMCRplus',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon='gmcr.ico' )
