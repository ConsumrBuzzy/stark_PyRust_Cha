import subprocess
import sys
import os
from pathlib import Path
import venv

REQUIRED_MAJOR = 3
REQUIRED_MINOR = 12

def check_python_version():
    """
    Checks if the *current* python interpreter matches the requirement.
    """
    current_version = sys.version_info[:2]
    if current_version != (REQUIRED_MAJOR, REQUIRED_MINOR):
        return False
    return True

def create_venv(venv_path):
    print(f"🔨 Creating virtual environment at {venv_path} using Python {REQUIRED_MAJOR}.{REQUIRED_MINOR}...")
    
    # Try using the 'py' launcher on Windows to find the specific version
    if sys.platform == "win32":
        try:
            subprocess.check_call(["py", f"-{REQUIRED_MAJOR}.{REQUIRED_MINOR}", "-m", "venv", str(venv_path)])
            print("✅ Virtual environment created.")
            return
        except subprocess.CalledProcessError:
            print(f"⚠️  'py -{REQUIRED_MAJOR}.{REQUIRED_MINOR}' failed. Falling back to current interpreter...")
        except FileNotFoundError:
             print("⚠️  'py' launcher not found. Falling back to current interpreter...")

    # Fallback: Use the current interpreter if it matches
    if check_python_version():
         venv.create(venv_path, with_pip=True)
         print("✅ Virtual environment created using current interpreter.")
    else:
        print(f"❌ Error: Current Python is {sys.version_info[:2]}, but {REQUIRED_MAJOR}.{REQUIRED_MINOR} is required.")
        print(f"   Please install Python {REQUIRED_MAJOR}.{REQUIRED_MINOR} or run this script with it.")
        sys.exit(1)

def install_dependencies(venv_python):
    print("📦 Installing dependencies...")
    subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([venv_python, "-m", "pip", "install", "maturin", "typer", "rich", "pydantic"])
    print("✅ Dependencies installed.")

def main():
    project_root = Path(__file__).parent
    venv_dir = project_root / "venv"
    
    # Determine path to the venv's python executable
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"

    if not venv_dir.exists():
        create_venv(venv_dir)
    
    if not venv_python.exists():
        print(f"❌ Error: Python binary not found at {venv_python}")
        sys.exit(1)

    install_dependencies(str(venv_python))
    
    print("\n🚀 Environment setup complete.")
    print(f"   To activate: .\\venv\\Scripts\\activate (Windows)")
    print("   Then run: ..\\venv\\Scripts\\python build_rust.py (or just python build_rust.py if activated)")

if __name__ == "__main__":
    main()
