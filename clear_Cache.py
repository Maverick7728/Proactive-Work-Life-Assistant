import os
import shutil
from pathlib import Path

# List of relative paths to remove in the project directory
PROJECT_CACHE_DIRS = [
    '__pycache__',
    '.pytest_cache',
    'logs',
    os.path.join('.streamlit', 'cache'),
    os.path.join('.streamlit', 'logs'),
]

# File patterns to remove
PROJECT_CACHE_PATTERNS = ['*.pyc']

# Streamlit global cache/logs in user home
HOME_CACHE_DIRS = [
    os.path.join('.streamlit', 'cache'),
    os.path.join('.streamlit', 'logs'),
]

def remove_dir(path):
    if path.exists() and path.is_dir():
        print(f"Deleting directory: {path}")
        shutil.rmtree(path, ignore_errors=True)
    else:
        pass  # Directory does not exist

def remove_file(path):
    if path.exists() and path.is_file():
        print(f"Deleting file: {path}")
        path.unlink()

def clear_project_cache(base_path):
    # Remove cache/log dirs recursively
    for rel_dir in PROJECT_CACHE_DIRS:
        for dir_path in base_path.rglob(rel_dir):
            remove_dir(dir_path)
    # Remove .pyc files
    for pattern in PROJECT_CACHE_PATTERNS:
        for file_path in base_path.rglob(pattern):
            remove_file(file_path)

def clear_home_streamlit_cache():
    home = Path.home()
    for rel_dir in HOME_CACHE_DIRS:
        dir_path = home / rel_dir
        remove_dir(dir_path)

def main():
    base_path = Path(__file__).parent.resolve()
    print(f"Clearing cache in project directory: {base_path}")
    clear_project_cache(base_path)
    print("\nClearing Streamlit cache/logs in user home directory...")
    clear_home_streamlit_cache()
    print("\nCache clearing complete.")

if __name__ == "__main__":
    main() 