# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['e:\\المشروع\\SIM-NET Ai\\SIM-NET\\backend\\app.py'],
    pathex=[],
    binaries=[],
    datas=[('e:\\المشروع\\SIM-NET Ai\\SIM-NET\\frontend', 'frontend')],
    hiddenimports=['engineio.async_drivers.threading', 'PIL'],
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
    name='SIM-NET-AI',
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
    icon=['e:\\المشروع\\SIM-NET Ai\\SIM-NET\\assets\\icon.ico'],
)
