import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🦀 Building stark_PyRust_Chain Rust Core...")
    
    # Ensure we are in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Check for virtual environment
    if sys.prefix == sys.base_prefix:
        print("⚠️  Warning: Not running in a virtual environment.")
        
    # Manually set VIRTUAL_ENV if it's not set
    # This helps maturin detect the environment when running via full path
    env = os.environ.copy()
    if "VIRTUAL_ENV" not in env:
        venv_path = project_root / "venv"
        env["VIRTUAL_ENV"] = str(venv_path)
        env["PATH"] = str(venv_path / "Scripts") + os.pathsep + env["PATH"]
        print(f"🔧 Manually injecting VIRTUAL_ENV={venv_path}")

    try:
        # Build with Maturin
        cmd = [sys.executable, "-m", "maturin", "develop", "--release"]
        
        print(f"   Executing: {' '.join(cmd)}")
        subprocess.check_call(cmd, env=env)
        print("✅ Rust extension built and installed successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
