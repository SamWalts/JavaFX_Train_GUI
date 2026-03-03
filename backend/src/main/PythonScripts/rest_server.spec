# rest_server.spec — PyInstaller recipe
# Produces a SINGLE self-contained executable (--onefile mode).
#
# Why --onefile instead of --onedir?
#   --onedir bundles Python.framework as a visible directory tree.
#   macOS jpackage calls codesign on --app-content and fails because
#   Python.framework/Python has an "ambiguous bundle format" (app vs framework).
#   --onefile wraps everything into one binary — no exposed Python.framework,
#   no codesign problem.  Cold-start is ~2-3s slower (extraction to /tmp) but
#   that is acceptable since awaitHealthy() already waits up to 30s.
#
# Run with:
#   pyinstaller rest_server.spec --noconfirm
#
# Output: dist/rest_server        (single binary, no folder)
#         dist/rest_server.exe    (Windows)

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    # The script to freeze
    ['rest_server.py'],
    pathex=[],
    binaries=[],
    # Data files to bundle alongside the executable.
    # Format: (source_path, destination_folder_inside_bundle)
    # We include the seed DB so first-run seeding works even offline.
    datas=[
        ('rest_server.db.json', '.'),   # seed database bundled inside the binary
    ],
    hiddenimports=[
        # TinyDB uses importlib to load storage backends dynamically —
        # PyInstaller can't see those imports statically, so we declare them.
        'tinydb',
        'tinydb.storages',
        'tinydb.middlewares',
        'tinydb.database',
        'tinydb.table',
        'tinydb.queries',
        # Flask internals that get missed by static analysis
        'flask',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.routing',
        'werkzeug.exceptions',
        'jinja2',
        'jinja2.ext',
        'click',
        # waitress (production WSGI server, optional fallback)
        'waitress',
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
    a.binaries,      # included directly for --onefile
    a.zipfiles,
    a.datas,
    [],
    name='rest_server',
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
    # onefile=True is implicit when no COLLECT() is present
)
# NOTE: No COLLECT() call — this is what makes it --onefile
