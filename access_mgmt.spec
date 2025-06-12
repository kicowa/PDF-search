# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Zbierz wszystkie moduły i dane Streamlit
streamlit_data = collect_data_files('streamlit')
streamlit_hidden_imports = collect_submodules('streamlit')

a = Analysis(
    ['nowy skrypt wersja 2.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('POC.xlsx', '.'),  # Dołącz plik Excel
        *streamlit_data,    # Dodaj dane Streamlit
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'openpyxl',
        'PIL',
        'packaging',
        'importlib_metadata',
        *streamlit_hidden_imports,  # Dodaj wszystkie podmoduły Streamlit
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Access Management',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Access Management',
) 