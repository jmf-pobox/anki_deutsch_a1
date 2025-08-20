#!/usr/bin/env python3
"""Migration script to convert services to lazy loading pattern.

This script helps migrate the AudioService and PexelsService to use
lazy initialization, improving test isolation and CI/CD compatibility.

Usage:
    python scripts/migrate_to_lazy_loading.py [--check-only]

Options:
    --check-only    Only check if migration is needed, don't make changes
"""

import argparse
import ast
import sys
from pathlib import Path


class LazyLoadingChecker(ast.NodeVisitor):
    """AST visitor to check for eager service initialization."""

    def __init__(self):
        self.eager_initializations = []
        self.lazy_properties = []

    def visit_FunctionDef(self, node):
        """Check __init__ methods for eager initialization."""
        if node.name == "__init__":
            for child in ast.walk(node):
                if isinstance(child, ast.Assign):
                    # Check for boto3.client() calls
                    if isinstance(child.value, ast.Call):
                        if self._is_boto3_client_call(child.value):
                            self.eager_initializations.append(
                                (child.lineno, ast.unparse(child))
                            )
        self.generic_visit(node)

    def _is_boto3_client_call(self, node):
        """Check if a node is a boto3.client() call."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return node.func.value.id == "boto3" and node.func.attr == "client"
        return False


def check_file_for_eager_loading(file_path: Path) -> tuple[bool, list[str]]:
    """Check if a file uses eager service initialization.

    Args:
        file_path: Path to Python file to check

    Returns:
        Tuple of (needs_migration, list_of_issues)
    """
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        checker = LazyLoadingChecker()
        checker.visit(tree)

        issues = []
        if checker.eager_initializations:
            for lineno, code in checker.eager_initializations:
                issues.append(f"Line {lineno}: Eager initialization found: {code}")

        return len(issues) > 0, issues

    except SyntaxError as e:
        return False, [f"Syntax error in file: {e}"]
    except Exception as e:
        return False, [f"Error checking file: {e}"]


def migrate_to_lazy_loading(file_path: Path, dry_run: bool = False) -> bool:
    """Migrate a service file to use lazy loading.

    Args:
        file_path: Path to service file to migrate
        dry_run: If True, only report what would be changed

    Returns:
        bool: True if migration was successful
    """
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Migrating {file_path}")

    # Read the original file
    with open(file_path) as f:
        original_content = f.read()

    # Check if already using lazy loading
    if "_client: " in original_content and "property" in original_content:
        print("  ✓ File already uses lazy loading pattern")
        return True

    # Create modified content
    modified_content = original_content

    # Replace eager boto3.client initialization
    if "self.client = boto3.client" in modified_content:
        # Replace with lazy initialization
        modified_content = modified_content.replace(
            "self.client = boto3.client",
            "# Lazy initialization - client created on first use\n"
            "        self._client: PollyClient | None = None\n"
            "        # self.client = boto3.client  # OLD: Eager initialization",
        )

        # Add property for lazy loading
        property_code = '''
    @property
    def client(self) -> "PollyClient":
        """Lazy load the Polly client on first access."""
        if self._client is None:
            self._client = boto3.client("polly")
        return self._client
'''

        # Find the right place to insert the property (after __init__)
        lines = modified_content.split("\n")
        for i, line in enumerate(lines):
            if "def __init__" in line:
                # Find the end of __init__ method
                indent_level = len(line) - len(line.lstrip())
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(
                        " " * (indent_level + 4)
                    ):
                        # Found the end of __init__, insert property here
                        lines.insert(j, property_code)
                        break
                break

        modified_content = "\n".join(lines)

    if dry_run:
        print("  Would make the following changes:")
        print("  - Replace eager boto3.client() initialization with lazy property")
        print("  - Add @property client method for on-demand initialization")
        return True

    # Write the modified content
    with open(file_path, "w") as f:
        f.write(modified_content)

    print("  ✓ File migrated successfully")
    return True


def main():
    """Main migration script entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate services to lazy loading pattern"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check if migration is needed, don't make changes",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what changes would be made without modifying files",
    )
    args = parser.parse_args()

    # Find project root
    project_root = Path(__file__).parent.parent
    services_dir = project_root / "src" / "langlearn" / "services"

    # Target files for migration
    target_files = [
        services_dir / "audio.py",
        services_dir / "pexels_service.py",
    ]

    print("Lazy Loading Migration Tool")
    print("=" * 50)

    if args.check_only:
        print("\nChecking for services that need migration...")
        needs_migration = False

        for file_path in target_files:
            if file_path.exists():
                needs_update, issues = check_file_for_eager_loading(file_path)
                if needs_update:
                    needs_migration = True
                    print(f"\n❌ {file_path.name} needs migration:")
                    for issue in issues:
                        print(f"    {issue}")
                else:
                    print(f"\n✓ {file_path.name} - OK")

        if needs_migration:
            print("\n⚠️  Some files need migration to lazy loading pattern")
            print("Run without --check-only to perform migration")
            sys.exit(1)
        else:
            print("\n✅ All services already use lazy loading pattern")
            sys.exit(0)

    else:
        print("\nMigrating services to lazy loading pattern...")

        success = True
        for file_path in target_files:
            if file_path.exists():
                if not migrate_to_lazy_loading(file_path, dry_run=args.dry_run):
                    success = False
            else:
                print(f"\n⚠️  File not found: {file_path}")

        if success:
            print("\n✅ Migration completed successfully")
            print("\nNext steps:")
            print("1. Run tests to verify changes: hatch run test")
            print("2. Update CI/CD workflow with new configuration")
            print("3. Configure GitHub Secrets for integration tests")
        else:
            print("\n❌ Migration encountered errors")
            sys.exit(1)


if __name__ == "__main__":
    main()
