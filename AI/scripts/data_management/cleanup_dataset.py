#!/usr/bin/env python3
"""Clean up dataset by removing empty folders and consolidating duplicates."""
from pathlib import Path
import shutil

SAMPLE_DATA = Path('C:/Users/DELL/Desktop/new project/PoultryGuardAI/AI/sample_data')

print("Cleaning up sample_data...")
empty_dirs = []
name_counts = {}

for dir_path in sorted(SAMPLE_DATA.iterdir()):
    if not dir_path.is_dir():
        continue
    
    files = [f for f in dir_path.glob('*') if f.is_file()]
    count = len(files)
    
    if count == 0:
        empty_dirs.append(dir_path)
        print(f"  Empty: {dir_path.name}/")
    else:
        name_counts[dir_path.name] = count
        print(f"  {dir_path.name}: {count} images")

# Remove empty directories
for empty_dir in empty_dirs:
    shutil.rmtree(empty_dir)
    print(f"Removed: {empty_dir.name}")

print("\n✓ Cleanup complete")
print(f"Remaining classes: {len(name_counts)}")
