a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('images', 'images'),
        ('fonts/*', 'fonts'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

import sys

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MSH-Character-Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name='MSH-Character-Generator.app',
        icon='images/UPB_sm.icns',
        bundle_identifier='com.taskmasterx.mshcharactergenerator',
    )