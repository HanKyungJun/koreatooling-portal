# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('trico_client.py', '.'), ('daily_dlv_alert.py', '.'), ('zero_price_alert.py', '.')]
datas += collect_data_files('googleapiclient')


a = Analysis(
    ['erp_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['googleapiclient.discovery', 'google.auth.transport.requests', 'email.mime.multipart', 'email.mime.base', 'email.mime.text', 'email.encoders'],
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
    name='TricoERP',
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
