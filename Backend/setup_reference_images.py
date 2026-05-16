#!/usr/bin/env python3
"""
Save reference images to disease folders
Images are numbered 1-10 in order received

Mapping based on your disease list order:
1. Newcastle Disease  
2. Avian Influenza (Bird Flu)
3. Infectious Bursal Disease (Gumboro)
4. Marek's Disease
5. Fowl Pox
6. Infectious Bronchitis
7. Salmonellosis/Pullorum
8. Fowl Cholera
9. Mycoplasmosis (CRD)
10. Infectious Coryza
11. Healthy (no image provided - use bright white)
12. Coccidiosis (no image provided - use yellow)
"""

from pathlib import Path
import shutil
from PIL import Image
import numpy as np

# Disease mapping
DISEASE_MAPPING = {
    1: ("Newcastle disease", "Image 1: Dark bird"),
    2: ("Avian Influenza", "Image 2: Red inflammatory head"),
    3: ("Infectious Bursal Disease", "Image 3: Pale/weak bird"),
    4: ("Marek's Disease", "Image 4: Weak/depressed bird"),
    5: ("Fowl Pox", "Image 5: White bird with pink head"),
    6: ("Infectious Bronchitis", "Image 6: Brown chicken"),
    7: ("Salmonellosis/Pullorum", "Image 7: Sick bird - red head"),
    8: ("Fowl Cholera", "Image 8: Brown chicken - sick"),
    9: ("Mycoplasmosis (CRD)", "Image 9: White chicken"),
    10: ("Infectious Coryza", "Image 10: Bird with visible symptoms"),
}

print("Disease Reference Image Mapping")
print("=" * 60)
for idx, (disease, description) in DISEASE_MAPPING.items():
    print(f"{idx:2d}. {disease:35} - {description}")

# Note: Image files would be saved by the frontend or manually placed in folders
# This script shows the mapping structure

print("\n✓ Image mapping structure created")
print("\nNext step: Save your images to these folders:")
for disease_name in set(d for d, _ in DISEASE_MAPPING.values()):
    folder = Path("disease_references") / disease_name
    print(f"  - {folder}")
