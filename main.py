#!/usr/bin/env python3

import argparse
import json
import logging
import sys
from typing import Dict, List, Set, Tuple

try:
    from rich.console import Console
    from rich.table import Column, Table
except ImportError as e:
    print(f"Error: Missing dependencies. Please install them using: pip install rich")
    sys.exit(1)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PermissionDependencyUpdater:
    """
    Identifies dependencies between permissions and simulates updates to
    dependent permissions. This is a preview only: no permission
    configuration is changed by this tool.
    """

    def __init__(self, permission_map: Dict[str, Set[str]]):
        """
        Initializes the PermissionDependencyUpdater with a permission dependency map.

        Args:
            permission_map: A dictionary representing the permission dependencies.
                            Key: Permission name (str).
                            Value: A set of permissions (str) that the key permission depends on.
        """
        self.permission_map = permission_map
        self.console = Console()  # Initialize Rich Console

    def find_dependent_permissions(self, permission: str) -> Set[str]:
        """
        Finds all permissions that directly depend on a given permission.

        Args:
            permission: The permission to find dependencies for.

        Returns:
            A set of permissions that depend on the given permission.  Returns an empty set if no dependencies found,
            or if the permission does not exist in the map.
        """
        dependent_permissions: Set[str] = set()
        for perm, dependencies in self.permission_map.items():
            if permission in dependencies:
                dependent_permissions.add(perm)
        return dependent_permissions


    def update_dependent_permissions(self, permission: str, change_description: str) -> None:
        """
        Recursively simulates updates to all permissions that depend on a given permission.
        Nothing is modified; the tables printed are a preview of which
        permissions would be affected by the change.

        Args:
            permission: The permission that has been modified or deprecated.
            change_description: A description of the change that occurred (e.g., "deprecated", "modified").
        """

        dependent_permissions = self.find_dependent_permissions(permission)

        if not dependent_permissions:
            logging.info(f"No permissions depend on '{permission}'. No updates needed.")
            return

        logging.info(f"Simulating updates to dependent permissions for '{permission}' due to: {change_description}")

        table = Table(title=f"Simulated Permission Updates due to '{permission}' Change (preview only, nothing was changed)")
        table.add_column("Permission", style="cyan", no_wrap=True)
        table.add_column("Change Description", style="magenta")


        for dependent_permission in dependent_permissions:
            # Simulate updating the permission
            self._simulate_permission_update(dependent_permission, change_description)
            table.add_row(dependent_permission, change_description)

            # Recursively update permissions that depend on the current dependent permission
            self.update_dependent_permissions(dependent_permission, f"Indirectly due to '{permission}' being {change_description}")


        self.console.print(table)


    def _simulate_permission_update(self, permission: str, change_description: str) -> None:
        """
        Simulates the update of a permission.  In a real implementation, this would involve
        modifying the permission configuration.

        Args:
            permission: The permission to update.
            change_description: A description of the change being applied.
        """
        logging.info(f"Simulating update for permission '{permission}': {change_description}")
        # In a real application, this is where you would modify the permission's configuration.
        # For example, you might revoke access to a resource, or modify the scope of the permission.
        pass


def setup_argparse() -> argparse.ArgumentParser:
    """
    Sets up the command-line argument parser.

    Returns:
        An argparse.ArgumentParser object.
    """
    parser = argparse.ArgumentParser(
        description="Identifies dependent permissions and simulates (previews) updates based on changes to underlying permissions. Simulation only: no permission configuration is changed."
    )

    parser.add_argument(
        "--permission",
        type=str,
        required=True,
        help="The permission that has been modified or deprecated."
    )

    parser.add_argument(
        "--change-description",
        type=str,
        required=True,
        help="A description of the change that occurred (e.g., 'deprecated', 'modified')."
    )

    parser.add_argument(
        "--map-file",
        type=str,
        required=False,
        default=None,
        help="Path to a JSON file holding the permission map: an object mapping each permission name to a list of the permissions it depends on. When omitted, a small built in example map is used."
    )

    return parser



def validate_permission_map(permission_map: Dict[str, Set[str]]) -> bool:
    """
    Validates the permission map to ensure that it is well-formed.

    Args:
        permission_map: The permission map to validate.

    Returns:
        True if the permission map is valid, False otherwise.
    """
    if not isinstance(permission_map, dict):
        logging.error("Permission map must be a dictionary.")
        return False

    for permission, dependencies in permission_map.items():
        if not isinstance(permission, str):
            logging.error("Permission names must be strings.")
            return False
        if not isinstance(dependencies, set):
            logging.error(f"Dependencies for {permission} must be a set.")
            return False
        for dependency in dependencies:
            if not isinstance(dependency, str):
                logging.error(f"Dependency {dependency} for {permission} must be a string.")
                return False
    return True


def load_permission_map(map_file: str) -> Dict[str, Set[str]]:
    """
    Loads a permission map from a JSON file.

    The file must hold a JSON object mapping each permission name to a
    list of the permission names it depends on.

    Raises:
        OSError: If the file cannot be read.
        ValueError: If the file does not hold a map of that shape.
    """
    with open(map_file, "r") as f:
        raw = json.load(f)

    if not isinstance(raw, dict):
        raise ValueError("Permission map file must hold a JSON object.")

    permission_map: Dict[str, Set[str]] = {}
    for permission, dependencies in raw.items():
        if not isinstance(dependencies, list) or not all(
            isinstance(dep, str) for dep in dependencies
        ):
            raise ValueError(
                f"Dependencies for {permission} must be a list of permission names."
            )
        permission_map[permission] = set(dependencies)
    return permission_map


def permission_known(permission_map: Dict[str, Set[str]], permission: str) -> bool:
    """
    Returns True when the permission appears anywhere in the map, either
    as a permission name or as a dependency of another permission.
    """
    if permission in permission_map:
        return True
    return any(permission in deps for deps in permission_map.values())


def main() -> None:
    """
    Main function to execute the permission dependency update simulation.
    """
    parser = setup_argparse()
    args = parser.parse_args()


    if args.map_file:
        try:
            permission_map = load_permission_map(args.map_file)
        except (OSError, ValueError) as e:
            logging.error(f"Could not load permission map from '{args.map_file}': {e}")
            sys.exit(1)
    else:
        # Built in example permission map, used only when no --map-file is given.
        permission_map: Dict[str, Set[str]] = {
            "read_sensitive_data": {"authenticate_user"},
            "write_sensitive_data": {"read_sensitive_data", "authorize_user"},
            "admin_access": {"write_sensitive_data"},
            "authorize_user": {"authenticate_user"},
            "authenticate_user": set(),  # No dependencies
            "audit_logs": {"admin_access"}
        }
        logging.info("No --map-file given. Using the built in example permission map.")

    if not validate_permission_map(permission_map):
        logging.error("Invalid permission map. Exiting.")
        sys.exit(1)

    if not permission_known(permission_map, args.permission):
        logging.error(
            f"Permission '{args.permission}' not found in the permission map. "
            "No simulation was run."
        )
        sys.exit(1)

    updater = PermissionDependencyUpdater(permission_map)

    try:
        updater.update_dependent_permissions(args.permission, args.change_description)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

    logging.info("Simulation only: no permission configuration was changed.")


if __name__ == "__main__":
    main()