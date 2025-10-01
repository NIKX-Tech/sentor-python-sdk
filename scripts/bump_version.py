#!/usr/bin/env python3
"""
Version bumping script for sentor-ml-python-sdk
Usage: python scripts/bump_version.py [patch|minor|major]
"""

import re
import sys
from pathlib import Path


def get_current_version():
    """Extract current version from setup.py"""
    setup_py_path = Path("setup.py")
    if not setup_py_path.exists():
        raise FileNotFoundError("setup.py not found")

    with open(setup_py_path, "r") as f:
        content = f.read()

    # Look for version="x.y.z" pattern
    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find version in setup.py")

    return match.group(1)


def bump_version(version, bump_type):
    """Bump version based on type"""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")

    major, minor, patch = map(int, parts)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(
            f"Invalid bump type: {bump_type}. Use 'major', 'minor', or 'patch'"
        )

    return f"{major}.{minor}.{patch}"


def update_setup_py(new_version):
    """Update version in setup.py"""
    setup_py_path = Path("setup.py")

    with open(setup_py_path, "r") as f:
        content = f.read()

    # Replace version="x.y.z" with new version
    new_content = re.sub(
        r'version\s*=\s*["\'][^"\']+["\']', f'version="{new_version}"', content
    )

    with open(setup_py_path, "w") as f:
        f.write(new_content)

    print(f"Updated setup.py with version: {new_version}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py [patch|minor|major]")
        sys.exit(1)

    bump_type = sys.argv[1].lower()

    if bump_type not in ["patch", "minor", "major"]:
        print("Error: bump_type must be 'patch', 'minor', or 'major'")
        sys.exit(1)

    try:
        current_version = get_current_version()
        print(f"Current version: {current_version}")

        new_version = bump_version(current_version, bump_type)
        print(f"New version: {new_version}")

        update_setup_py(new_version)

        # Output the new version for GitHub Actions
        print(f"::set-output name=version::{new_version}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
