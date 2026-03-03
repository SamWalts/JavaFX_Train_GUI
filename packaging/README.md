# packaging/

This directory is the staging area used by `build-all.sh`.

`build-all.sh` copies the PyInstaller output here:
    dist/rest_server/  →  packaging/rest_server/

`jpackage` then picks it up via `--app-content packaging/rest_server`.

The `rest_server/` sub-folder itself is **not committed to Git** — it is
generated at build time and is listed in `.gitignore`.  Only this README is
tracked so the folder exists in the repo.

