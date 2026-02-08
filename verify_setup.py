"""
Quick verification script to ensure the refactored application is working correctly.
Run this to validate the setup before deploying.

Usage: python verify_setup.py
"""
import sys
import os
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ MISSING {description}: {filepath}")
        return False


def check_imports():
    """Check if all required modules can be imported."""
    modules_to_check = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('sqlalchemy', 'SQLAlchemy'),
    ]
    
    print("\n--- Checking Imports ---")
    all_ok = True
    for module, name in modules_to_check:
        try:
            __import__(module)
            print(f"✓ {name} is installed")
        except ImportError:
            print(f"✗ {name} is NOT installed")
            all_ok = False
    
    return all_ok


def check_structure():
    """Check if project structure is correct."""
    print("\n--- Checking Project Structure ---")
    
    files_to_check = [
        ('app.py', 'Main application file'),
        ('config.py', 'Configuration module'),
        ('models.py', 'Database models'),
        ('database.py', 'Database utilities'),
        ('routes.py', 'Application routes'),
        ('wsgi.py', 'WSGI entry point'),
        ('requirements.txt', 'Dependencies file'),
        ('.env.example', 'Environment template'),
        ('templates/base.html', 'Base template'),
        ('templates/index.html', 'Main template'),
        ('templates/fragments/rankings.html', 'Rankings fragment'),
        ('templates/fragments/wishes.html', 'Wishes fragment'),
        ('templates/fragments/scoreboard.html', 'Scoreboard fragment'),
        ('static/js/game.js', 'Game logic'),
    ]
    
    all_ok = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_ok = False
    
    return all_ok


def check_app_creation():
    """Try to create the Flask app."""
    print("\n--- Checking Application Factory ---")
    try:
        from app import create_app
        app = create_app('development')
        print(f"✓ Application factory works")
        print(f"  Debug mode: {app.debug}")
        print(f"  Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
        return True
    except Exception as e:
        print(f"✗ Failed to create app: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Badminton Daddy - Refactoring Verification")
    print("=" * 60)
    
    results = []
    
    # Check structure
    results.append(("Project Structure", check_structure()))
    
    # Check imports
    results.append(("Dependencies", check_imports()))
    
    # Check app creation
    results.append(("Application Factory", check_app_creation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for check_name, result in results:
        status = "PASS ✓" if result else "FAIL ✗"
        print(f"{check_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All checks passed! Application is ready to run.")
        print("\nTo start the development server:")
        print("  python app.py")
        sys.exit(0)
    else:
        print("✗ Some checks failed. Please review the issues above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Check file paths and directories")
        print("  3. Ensure Python 3.8+ is installed")
        sys.exit(1)


if __name__ == '__main__':
    main()
