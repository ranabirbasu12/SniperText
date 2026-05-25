# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\RanabirBasu\\Workspace\\SniperText\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\RanabirBasu\\Workspace\\SniperText\\assets\\icon.png', 'assets')],
    hiddenimports=['winocr', 'winrt.runtime', 'winrt.windows.media.ocr', 'winrt.windows.graphics.imaging', 'winrt.windows.storage.streams', 'winrt.windows.globalization', 'winrt.windows.foundation', 'winrt.windows.foundation.collections'],
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
    name='SniperText',
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
)
