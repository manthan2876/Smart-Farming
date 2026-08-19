import os
from pathlib import Path

# Updated to match your actual folder structure: F:\Projects\Crop Identification
PROJECT_SUBPATH = Path("Projects") / "Crop Identification"

def locate_project_root():
    # Automatically scan common drive letters for your project folder
    for drive in ["F:\\", "D:\\", "E:\\", "G:\\", "C:\\"]:
        candidate = Path(drive) / PROJECT_SUBPATH
        if candidate.exists():
            return candidate
    
    # Fallback: if running directly from inside the notebooks folder, find root dynamically
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if parent.name == "Crop Identification":
            return parent
            
    raise FileNotFoundError("Could not find project root on any common drive letters or current path!")

PROJECT_ROOT = locate_project_root()
RAW_ROOT = PROJECT_ROOT / "Final Datasets"
MODELS_DIR = PROJECT_ROOT / "models"
MANIFEST_PATH = PROJECT_ROOT / "notebooks" / "manifest.csv"

if __name__ == "__main__":
    print(f"Project Root Found: {PROJECT_ROOT}")
    print(f"Raw Root Exists: {RAW_ROOT.exists()}")
    print(f"Manifest Exists: {MANIFEST_PATH.exists()}")