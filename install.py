"""
Stable-TS GUI Installer
Checks for and installs all required dependencies.
Run this script first before launching the application.
"""

import subprocess
import sys
import os
import shutil

# Required packages and their pip names
REQUIRED_PACKAGES = [
    ("customtkinter", "customtkinter"),
    ("tkinterdnd2", "tkinterdnd2"),
    ("stable_whisper", "stable-ts"),
]

# Optional: PyTorch with CUDA support
PYTORCH_CUDA_COMMAND = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
PYTORCH_CPU_COMMAND = "pip install torch torchvision torchaudio"


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_status(name, status, message=""):
    symbol = "✓" if status else "✗"
    color_start = ""
    color_end = ""
    if message:
        print(f"  [{symbol}] {name}: {message}")
    else:
        print(f"  [{symbol}] {name}")


def check_python_version():
    """Check if Python version is compatible."""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_status("Python", True, f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_status("Python", False, f"{version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False


def check_ffmpeg():
    """Check if ffmpeg is installed and in PATH."""
    print_header("Checking FFmpeg")
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print_status("ffmpeg", True, ffmpeg_path)
        return True
    else:
        print_status("ffmpeg", False, "Not found in PATH")
        print("\n  FFmpeg is required for audio processing.")
        print("  Installation instructions:")
        print("    Windows: Download from https://www.gyan.dev/ffmpeg/builds/")
        print("             Extract and add 'bin' folder to system PATH")
        print("    Mac:     brew install ffmpeg")
        print("    Linux:   sudo apt install ffmpeg")
        return False


def check_package(import_name):
    """Check if a package is installed."""
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def install_package(pip_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def check_and_install_packages():
    """Check and install required Python packages."""
    print_header("Checking Python Packages")
    
    all_installed = True
    packages_to_install = []
    
    for import_name, pip_name in REQUIRED_PACKAGES:
        if check_package(import_name):
            print_status(import_name, True, "Installed")
        else:
            print_status(import_name, False, "Not installed")
            packages_to_install.append((import_name, pip_name))
            all_installed = False
    
    if packages_to_install:
        print("\n  Some packages need to be installed.")
        response = input("  Install missing packages? [Y/n]: ").strip().lower()
        
        if response != 'n':
            print("\n  Installing packages...")
            for import_name, pip_name in packages_to_install:
                print(f"    Installing {pip_name}...", end=" ", flush=True)
                if install_package(pip_name):
                    print("Done!")
                else:
                    print("FAILED!")
                    all_installed = False
    
    return all_installed


def detect_nvidia_gpu():
    """Detect if an NVIDIA GPU is present using nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            gpu_names = result.stdout.strip().split('\n')
            return gpu_names
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return None


def check_pytorch():
    """Check PyTorch installation and CUDA availability."""
    print_header("Checking PyTorch & GPU")
    
    # First, detect NVIDIA GPU regardless of PyTorch installation
    nvidia_gpus = detect_nvidia_gpu()
    if nvidia_gpus:
        print_status("NVIDIA GPU", True, ", ".join(nvidia_gpus))
        has_nvidia = True
    else:
        print_status("NVIDIA GPU", False, "Not detected (nvidia-smi not found or no GPU)")
        has_nvidia = False
    
    try:
        import torch
        print_status("PyTorch", True, f"Version {torch.__version__}")
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print_status("CUDA Support", True, f"Enabled ({gpu_name})")
        else:
            print_status("CUDA Support", False, "Not available in current PyTorch")
            if has_nvidia:
                print("\n  You have an NVIDIA GPU but PyTorch was installed without CUDA.")
                print("  For GPU acceleration, reinstall PyTorch with CUDA:")
                print(f"    pip uninstall torch torchvision torchaudio -y")
                print(f"    {PYTORCH_CUDA_COMMAND}")
                response = input("\n  Reinstall PyTorch with CUDA support now? [Y/n]: ").strip().lower()
                if response != 'n':
                    print("\n  Reinstalling PyTorch with CUDA...")
                    subprocess.call("pip uninstall torch torchvision torchaudio -y", shell=True)
                    subprocess.call(PYTORCH_CUDA_COMMAND, shell=True)
        
        return True
        
    except ImportError:
        print_status("PyTorch", False, "Not installed")
        print("\n  PyTorch is required for Whisper models.")
        
        if has_nvidia:
            print(f"\n  NVIDIA GPU detected! Recommended: Install with CUDA for GPU acceleration.")
            print("  Choose installation type:")
            print("    1. CUDA/GPU (recommended - faster transcription)")
            print("    2. CPU only (slower, but works everywhere)")
            print("    3. Skip (install manually later)")
            
            choice = input("  Enter choice [1/2/3]: ").strip()
            
            if choice == "1" or choice == "":
                print("\n  Installing PyTorch with CUDA support...")
                subprocess.call(PYTORCH_CUDA_COMMAND, shell=True)
                return True
            elif choice == "2":
                print("\n  Installing PyTorch (CPU only)...")
                subprocess.call(PYTORCH_CPU_COMMAND, shell=True)
                return True
            else:
                print("  Skipping PyTorch installation.")
                return False
        else:
            print("\n  No NVIDIA GPU detected. Installing CPU version.")
            print("  Choose installation type:")
            print("    1. CPU only (default)")
            print("    2. CUDA/GPU (only if you have an NVIDIA GPU)")
            print("    3. Skip (install manually later)")
            
            choice = input("  Enter choice [1/2/3]: ").strip()
            
            if choice == "1" or choice == "":
                print("\n  Installing PyTorch (CPU)...")
                subprocess.call(PYTORCH_CPU_COMMAND, shell=True)
                return True
            elif choice == "2":
                print("\n  Installing PyTorch with CUDA...")
                subprocess.call(PYTORCH_CUDA_COMMAND, shell=True)
                return True
            else:
                print("  Skipping PyTorch installation.")
                return False


def check_stable_whisper():
    """Verify stable-ts is working correctly."""
    print_header("Verifying Stable-TS")
    
    try:
        import stable_whisper
        print_status("stable-ts", True, "Import successful")
        return True
    except ImportError as e:
        print_status("stable-ts", False, str(e))
        return False
    except Exception as e:
        print_status("stable-ts", False, f"Error: {str(e)}")
        return False


def main():
    print("\n" + "=" * 60)
    print("       STABLE-TS GUI INSTALLER")
    print("=" * 60)
    print("\nThis script will check and install all required dependencies.")
    print("Press Ctrl+C at any time to cancel.\n")
    
    all_ok = True
    
    # Check Python version
    if not check_python_version():
        print("\nPlease upgrade Python to version 3.8 or higher.")
        return False
    
    # Check ffmpeg
    if not check_ffmpeg():
        all_ok = False
    
    # Check PyTorch first (required for stable-ts)
    if not check_pytorch():
        all_ok = False
    
    # Check and install other packages
    if not check_and_install_packages():
        all_ok = False
    
    # Verify stable-ts
    if not check_stable_whisper():
        all_ok = False
    
    # Final summary
    print_header("Installation Summary")
    
    if all_ok:
        print("  All dependencies are installed correctly!")
        print("\n  To launch the application, run:")
        print("    python main.py")
        print()
    else:
        print("  Some dependencies are missing or failed to install.")
        print("  Please review the errors above and try again.")
        print()
    
    return all_ok


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled.")
        sys.exit(1)
