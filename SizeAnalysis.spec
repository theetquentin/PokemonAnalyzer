# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6.QtWebEngine', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.Qt3DInput', 'PySide6.Qt3DCore', 'PySide6.Qt3DExtras', 'PySide6.Qt3DRender', 'PySide6.Qt3DLogic', 'PySide6.QtQuick', 'PySide6.QtQuickWidgets', 'PySide6.QtQuickShapes', 'PySide6.QtQml', 'PySide6.QtSql', 'PySide6.QtTest', 'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets', 'PySide6.QtTextToSpeech', 'PySide6.QtDesigner', 'PySide6.QtHelp', 'PySide6.QtSensors', 'PySide6.QtSerialPort', 'PySide6.QtCharts', 'PySide6.QtSpatialAudio', 'PySide6.QtBluetooth', 'PySide6.QtNfc', 'PySide6.QtLocation', 'PySide6.QtPositioning', 'PySide6.QtWebChannel', 'PySide6.QtWebSockets'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SizeAnalysis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SizeAnalysis',
)
