# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('Images', 'Images'), ('alembic', 'alembic'), ('alembic.ini', '.'), ('app version.txt', '.'), ('languages.json', '.')],
    hiddenimports=['logging.config'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide6.support', 'pyparsing', 'numpy', 'pycparser', 'mysql', 'MySQLdb', 'xml', 'multiprocessing', 'lzma', 'http', 'greenlet', 'fractions', 'hmac', 'getopt', 'bz2', 'zoneinfo', 'tracemalloc'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='main',
)
