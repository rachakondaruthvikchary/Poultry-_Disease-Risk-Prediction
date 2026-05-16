#!/usr/bin/env python3
"""Delete all folders except Infectious-Bursal-Disease and Healthy."""
import shutil
from pathlib import Path

SAMPLE_DATA = Path('C:/Users/DELL/Desktop/new project/PoultryGuardAI/AI/sample_data')

# Folders to keep
KEEP = {'Infectious-Bursal-Disease', 'Healthy'}

print('Deleting folders...')
deleted = []
for item in SAMPLE_DATA.iterdir():
    if item.is_dir() and item.name not in KEEP:
        try:
            shutil.rmtree(item)
            deleted.append(item.name)
            print(f'  ✓ Deleted: {item.name}')
        except Exception as e:
            print(f'  ✗ Failed to delete {item.name}: {e}')

print(f'\nTotal deleted: {len(deleted)}')
print('\nRemaining folders:')
for item in sorted(SAMPLE_DATA.iterdir()):
    if item.is_dir():
        count = len([f for f in item.glob('*') if f.is_file()])
        print(f'  {item.name}: {count} images')
