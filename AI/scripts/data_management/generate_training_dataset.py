#!/usr/bin/env python3
"""
Generate synthetic training images for ALL 12 diseases to populate AI/sample_data
This ensures we have balanced training data for all disease classes
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random

random.seed(42)
np.random.seed(42)

def generate_disease_image(disease_name: str, width: int = 224, height: int = 224, variation: int = 0) -> Image.Image:
    """Generate distinctive synthetic disease images"""
    
    # Add randomness for variation
    np.random.seed(42 + variation)
    random.seed(42 + variation)
    
    img = Image.new("RGB", (width, height), (240, 240, 240))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    if disease_name == "Newcastle disease":
        draw.rectangle([50, 50, 200, 200], fill=(30, 30, 40, 255))
        draw.ellipse([60, 80, 180, 140], fill=(50, 50, 70, 255))
        draw.ellipse([90, 40, 140, 80], fill=(20, 20, 30, 255))
        draw.line([(110, 80), (120, 120)], fill=(40, 40, 50, 255), width=8)
        
    elif disease_name == "Avian Influenza":
        draw.rectangle([50, 50, 200, 200], fill=(180, 100, 100, 255))
        draw.ellipse([70, 60, 190, 180], fill=(200, 120, 100, 255))
        draw.ellipse([85, 50, 155, 90], fill=(200, 60, 60, 255))
        draw.ellipse([90, 55, 150, 85], fill=(220, 80, 80, 255))
        draw.ellipse([95, 58, 145, 82], fill=(240, 100, 100, 255))
        
    elif disease_name == "Infectious Bursal Disease":
        draw.rectangle([50, 50, 200, 200], fill=(150, 140, 120, 255))
        draw.ellipse([70, 70, 180, 170], fill=(160, 150, 130, 255))
        for x in range(60, 190, 15):
            for y in range(60, 190, 15):
                draw.rectangle([x, y, x+10, y+10], fill=(120, 110, 90, 200))
        
    elif disease_name == "Marek's Disease":
        draw.rectangle([50, 50, 200, 200], fill=(110, 110, 120, 255))
        draw.ellipse([70, 80, 180, 160], fill=(130, 130, 140, 255))
        draw.line([(100, 100), (100, 180)], fill=(90, 90, 100, 255), width=15)
        draw.line([(160, 100), (165, 180)], fill=(150, 150, 160, 255), width=10)
        
    elif disease_name == "Fowl Pox":
        draw.rectangle([50, 50, 200, 200], fill=(245, 245, 245, 255))
        draw.ellipse([70, 80, 180, 160], fill=(240, 240, 240, 255))
        for _ in range(20):
            x = random.randint(80, 170)
            y = random.randint(70, 170)
            draw.ellipse([x, y, x+8, y+8], fill=(220, 180, 150, 255))
            draw.ellipse([x+1, y+1, x+6, y+6], fill=(200, 150, 120, 255))
        
    elif disease_name == "Infectious Bronchitis":
        draw.rectangle([50, 50, 200, 200], fill=(160, 100, 60, 255))
        draw.ellipse([70, 80, 180, 160], fill=(180, 120, 80, 255))
        draw.ellipse([100, 70, 140, 95], fill=(200, 150, 100, 255))
        for _ in range(10):
            y = random.randint(75, 100)
            draw.line([(120, y), (120, y+20)], fill=(150, 120, 90, 200), width=3)
        
    elif disease_name == "Salmonellosis-Pullorum":
        draw.rectangle([50, 50, 200, 200], fill=(180, 100, 80, 255))
        draw.ellipse([70, 80, 180, 160], fill=(200, 120, 90, 255))
        draw.ellipse([90, 50, 150, 90], fill=(200, 60, 40, 255))
        draw.ellipse([95, 55, 145, 85], fill=(220, 80, 60, 255))
        
    elif disease_name == "Fowl Cholera":
        draw.rectangle([50, 50, 200, 200], fill=(140, 90, 60, 255))
        draw.ellipse([70, 80, 180, 160], fill=(160, 110, 80, 255))
        for _ in range(15):
            x = random.randint(70, 170)
            y = random.randint(70, 170)
            draw.ellipse([x, y, x+12, y+12], fill=(60, 40, 20, 255))
            draw.ellipse([x+2, y+2, x+10, y+10], fill=(40, 20, 10, 255))
        
    elif disease_name == "Mycoplasmosis-CRD":
        draw.rectangle([50, 50, 200, 200], fill=(230, 230, 220, 255))
        draw.ellipse([70, 80, 180, 160], fill=(240, 240, 230, 255))
        draw.line([(100, 80), (105, 110)], fill=(180, 180, 200, 200), width=8)
        draw.line([(140, 80), (135, 110)], fill=(180, 180, 200, 200), width=8)
        draw.line([(120, 85), (118, 115)], fill=(160, 160, 190, 180), width=6)
        
    elif disease_name == "Infectious Coryza":
        draw.rectangle([50, 50, 200, 200], fill=(180, 150, 100, 255))
        draw.ellipse([70, 80, 180, 160], fill=(190, 160, 110, 255))
        draw.ellipse([80, 60, 160, 110], fill=(200, 160, 100, 255))
        draw.ellipse([85, 65, 155, 105], fill=(210, 170, 110, 255))
        draw.ellipse([90, 70, 150, 100], fill=(220, 180, 120, 255))
        
    elif disease_name == "Coccidiosis":
        draw.rectangle([50, 50, 200, 200], fill=(255, 250, 100, 255))
        draw.ellipse([70, 80, 180, 160], fill=(255, 240, 80, 255))
        for _ in range(25):
            x = random.randint(70, 170)
            y = random.randint(70, 170)
            draw.ellipse([x, y, x+5, y+5], fill=(200, 80, 40, 255))
        for _ in range(8):
            x = random.randint(70, 180)
            draw.line([(x, 100), (x+5, 140)], fill=(180, 60, 20, 200), width=2)
        
    elif disease_name == "Healthy":
        draw.rectangle([50, 50, 200, 200], fill=(200, 160, 100, 255))
        draw.ellipse([70, 80, 180, 160], fill=(210, 170, 110, 255))
        draw.ellipse([100, 60, 140, 90], fill=(200, 160, 100, 255))
        for x in range(70, 180, 20):
            for y in range(80, 160, 15):
                draw.line([(x, y), (x+8, y+6)], fill=(190, 150, 90, 150), width=2)
    
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    return img


def main():
    diseases = [
        "Newcastle disease",
        "Avian Influenza",
        "Infectious Bursal Disease",
        "Marek's Disease",
        "Fowl Pox",
        "Infectious Bronchitis",
        "Salmonellosis-Pullorum",
        "Fowl Cholera",
        "Mycoplasmosis-CRD",
        "Infectious Coryza",
        "Coccidiosis",
        "Healthy",
    ]
    
    base_dir = Path(__file__).parent / "sample_data"
    
    print("🖼️  Generating synthetic training images for all 12 diseases...")
    print("=" * 70)
    
    count = 0
    for disease in diseases:
        # Use folder name exactly as it appears in sample_data
        disease_dir = base_dir / disease
        disease_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate 150 images per disease for balanced training
        for idx in range(150):
            img = generate_disease_image(disease, variation=idx)
            filename = disease_dir / f"synth_{idx:04d}.jpg"
            # Ensure RGB mode and save with higher quality
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(filename, "JPEG", quality=95, optimize=False)
            count += 1
            
            if (idx + 1) % 30 == 0:
                print(f"  ✓ {disease}: {idx + 1}/150 images")
    
    print("=" * 70)
    print(f"✅ Generated {count} synthetic training images for all 12 diseases")
    print(f"   Each disease folder now has 150 images")
    print(f"\n📊 Dataset is now balanced and ready for training!")


if __name__ == "__main__":
    main()
