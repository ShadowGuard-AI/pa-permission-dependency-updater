# pa-permission-dependency-updater
Simulation only: this tool changes no permission configuration. It identifies dependencies between permissions (e.g., permission A is required for permission B to function) and previews which dependent permissions would be affected when an underlying permission is modified or deprecated. Every table it prints is a simulated preview, headed as simulated, and the run ends by stating that no configuration was changed. Use the preview to plan a real change in your own permission system; this tool does not make that change. - Focused on Tools for analyzing and assessing file system permissions

## Install
`git clone https://github.com/ShadowGuard-AI/pa-permission-dependency-updater`

## Usage
`python3 main.py --permission NAME --change-description TEXT [--map-file PATH]`

## Parameters
- `-h`: Show help message and exit
- `--permission`: (required) The permission that has been modified or deprecated.
- `--change-description`: (required) A description of the change that occurred (e.g., 'deprecated', 'modified').
- `--map-file`: (optional, default none) Path to a JSON file holding the permission map: an object mapping each permission name to a list of the permissions it depends on. When omitted, a small built in example map is used and the run says so.

## Behavior notes
- If the named permission does not appear anywhere in the map, as a permission name or as a dependency, the run prints a not found error and exits 1. A permission that is in the map but has no dependents prints a no updates needed line and exits 0.
- The only dependency is `rich` (see requirements.txt). Earlier versions also required `pathspec`, which the code never used; that requirement has been removed.

## License
See LICENSE.
