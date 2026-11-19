# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

a = Analysis(
    ['main/app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('main/settings.json', 'main'),
    ],
    hiddenimports=['PIL', 'PIL.ImageTk', 'PIL.ImageDraw', 'tkinterdnd2'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Image-Pixelator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    noconfirm=True,
    append_pkg=False,
)
