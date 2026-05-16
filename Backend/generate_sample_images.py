#!/usr/bin/env python3
"""Generate sample disease reference images for testing"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Disease folders
diseases = {
    "Newcastle disease": (40, 30, 20),  # Dark brown
    "Avian Influenza": (180, 80, 80),   # Bright red (inflammation)
    "Infectious Bursal Disease": (120, 140, 100),  # Pale greenish
    "Marek's Disease": (100, 90, 85),   # Grayish
    "Fowl Pox": (150, 100, 80),         # Brown/tan
    "Infectious Bronchitis": (140, 120, 110),  # Brownish
    "Salmonellosis-Pullorum": (160, 100, 100),  # Reddish-brown
    "Fowl Cholera": (110, 100, 120),    # Blueish-gray
    "Mycoplasmosis-CRD": (130, 140, 130),  # Grayish-green
    "Infectious Coryza": (150, 120, 100),  # Brown
    "Coccidiosis": (200, 180, 100),     # Yellow-brown
    "Healthy": (255, 200, 150),         # Flesh tone
}

base_folder = Path(__file__).parent / "disease_references"
base_folder.mkdir(exist_ok=True)

for disease, color in diseases.items():
    disease_folder = base_folder / disease
    disease_folder.mkdir(exist_ok=True)
    
    # Create 2 sample images per disease
    for i in range(1, 3):
        img = Image.new('RGB', (224, 224), color)
        draw = ImageDraw.Draw(img)
        
        # Add text label
        text = f"{disease}\n(Sample {i})"
        try:
            # Try to use a larger font if available
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (224 - text_width) // 2
        y = (224 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        img_path = disease_folder / f"sample_{i}.jpg"
        img.save(img_path)
        print(f"✓ Created: {img_path}")

print("\n✅ Sample disease images created successfully!")
print(f"Location: {base_folder}")
