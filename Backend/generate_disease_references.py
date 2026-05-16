#!/usr/bin/env python3
"""
Generate synthetic reference images for disease detection
These serve as training examples for the image matching system
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

def generate_disease_image(disease_name: str, width: int = 224, height: int = 224) -> Image.Image:
    """Generate distinctive synthetic disease images with disease-specific visual patterns"""
    
    # Create base image
    img = Image.new("RGB", (width, height), (240, 240, 240))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Disease-specific characteristics
    if disease_name == "Newcastle disease":
        # Dark depressed bird - dark grays/blacks
        draw.rectangle([50, 50, 200, 200], fill=(30, 30, 40, 255))
        draw.ellipse([60, 80, 180, 140], fill=(50, 50, 70, 255))
        # Dark head
        draw.ellipse([90, 40, 140, 80], fill=(20, 20, 30, 255))
        # Neurological signs - twisted neck lines
        draw.line([(110, 80), (120, 120)], fill=(40, 40, 50, 255), width=8)
        
    elif disease_name == "Avian Influenza":
        # Severe inflammation - red/purple head
        draw.rectangle([50, 50, 200, 200], fill=(180, 100, 100, 255))
        draw.ellipse([70, 60, 190, 180], fill=(200, 120, 100, 255))
        # Inflamed head with cyanosis
        draw.ellipse([85, 50, 155, 90], fill=(200, 60, 60, 255))
        draw.ellipse([90, 55, 150, 85], fill=(220, 80, 80, 255))
        draw.ellipse([95, 58, 145, 82], fill=(240, 100, 100, 255))
        
    elif disease_name == "Infectious Bursal Disease":
        # Pale, weak appearance
        draw.rectangle([50, 50, 200, 200], fill=(150, 140, 120, 255))
        draw.ellipse([70, 70, 180, 170], fill=(160, 150, 130, 255))
        # Feather loss pattern
        for x in range(60, 190, 15):
            for y in range(60, 190, 15):
                draw.rectangle([x, y, x+10, y+10], fill=(120, 110, 90, 200))
        
    elif disease_name == "Marek's Disease":
        # Gray with nerve damage indicators
        draw.rectangle([50, 50, 200, 200], fill=(110, 110, 120, 255))
        draw.ellipse([70, 80, 180, 160], fill=(130, 130, 140, 255))
        # Paralysis signs - asymmetry
        draw.line([(100, 100), (100, 180)], fill=(90, 90, 100, 255), width=15)
        draw.line([(160, 100), (165, 180)], fill=(150, 150, 160, 255), width=10)
        
    elif disease_name == "Fowl Pox":
        # White bird with scabby lesions
        draw.rectangle([50, 50, 200, 200], fill=(245, 245, 245, 255))
        draw.ellipse([70, 80, 180, 160], fill=(240, 240, 240, 255))
        # Pox lesions on face/body
        for _ in range(20):
            x = random.randint(80, 170)
            y = random.randint(70, 170)
            draw.ellipse([x, y, x+8, y+8], fill=(220, 180, 150, 255))
            draw.ellipse([x+1, y+1, x+6, y+6], fill=(200, 150, 120, 255))
        
    elif disease_name == "Infectious Bronchitis":
        # Brown bird with discharge
        draw.rectangle([50, 50, 200, 200], fill=(160, 100, 60, 255))
        draw.ellipse([70, 80, 180, 160], fill=(180, 120, 80, 255))
        # Nasal discharge and eye swelling
        draw.ellipse([100, 70, 140, 95], fill=(200, 150, 100, 255))
        # Discharge streaks
        for _ in range(10):
            y = random.randint(75, 100)
            draw.line([(120, y), (120, y+20)], fill=(150, 120, 90, 200), width=3)
        
    elif disease_name == "Salmonellosis-Pullorum":
        # Red inflamed head with sick appearance
        draw.rectangle([50, 50, 200, 200], fill=(180, 100, 80, 255))
        draw.ellipse([70, 80, 180, 160], fill=(200, 120, 90, 255))
        # Severe head inflammation
        draw.ellipse([90, 50, 150, 90], fill=(200, 60, 40, 255))
        draw.ellipse([95, 55, 145, 85], fill=(220, 80, 60, 255))
        
    elif disease_name == "Fowl Cholera":
        # Brown with septic spots and discharge
        draw.rectangle([50, 50, 200, 200], fill=(140, 90, 60, 255))
        draw.ellipse([70, 80, 180, 160], fill=(160, 110, 80, 255))
        # Dark septic necrotic areas
        for _ in range(15):
            x = random.randint(70, 170)
            y = random.randint(70, 170)
            draw.ellipse([x, y, x+12, y+12], fill=(60, 40, 20, 255))
            draw.ellipse([x+2, y+2, x+10, y+10], fill=(40, 20, 10, 255))
        
    elif disease_name == "Mycoplasmosis-CRD":
        # White with respiratory fluid
        draw.rectangle([50, 50, 200, 200], fill=(230, 230, 220, 255))
        draw.ellipse([70, 80, 180, 160], fill=(240, 240, 230, 255))
        # Thick mucous discharge patterns
        draw.line([(100, 80), (105, 110)], fill=(180, 180, 200, 200), width=8)
        draw.line([(140, 80), (135, 110)], fill=(180, 180, 200, 200), width=8)
        draw.line([(120, 85), (118, 115)], fill=(160, 160, 190, 180), width=6)
        
    elif disease_name == "Infectious Coryza":
        # Swollen face/nasal area
        draw.rectangle([50, 50, 200, 200], fill=(180, 150, 100, 255))
        draw.ellipse([70, 80, 180, 160], fill=(190, 160, 110, 255))
        # Severe facial/ocular edema
        draw.ellipse([80, 60, 160, 110], fill=(200, 160, 100, 255))
        draw.ellipse([85, 65, 155, 105], fill=(210, 170, 110, 255))
        draw.ellipse([90, 70, 150, 100], fill=(220, 180, 120, 255))
        
    elif disease_name == "Coccidiosis":
        # Yellowish with bloody mucous appearance
        draw.rectangle([50, 50, 200, 200], fill=(255, 250, 100, 255))
        draw.ellipse([70, 80, 180, 160], fill=(255, 240, 80, 255))
        # Hemorrhagic intestinal appearance
        for _ in range(25):
            x = random.randint(70, 170)
            y = random.randint(70, 170)
            draw.ellipse([x, y, x+5, y+5], fill=(200, 80, 40, 255))
        # Bloody streaks
        for _ in range(8):
            x = random.randint(70, 180)
            draw.line([(x, 100), (x+5, 140)], fill=(180, 60, 20, 200), width=2)
        
    elif disease_name == "Healthy":
        # Normal healthy brown chicken
        draw.rectangle([50, 50, 200, 200], fill=(200, 160, 100, 255))
        draw.ellipse([70, 80, 180, 160], fill=(210, 170, 110, 255))
        draw.ellipse([100, 60, 140, 90], fill=(200, 160, 100, 255))
        # Normal feather pattern
        for x in range(70, 180, 20):
            for y in range(80, 160, 15):
                draw.line([(x, y), (x+8, y+6)], fill=(190, 150, 90, 150), width=2)
    
    # Slight blur for realism
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    
    return img


def main():
    """Generate and save reference images for all diseases"""
    
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
    
    base_dir = Path(__file__).parent / "disease_references"
    base_dir.mkdir(exist_ok=True)
    
    print("Generating synthetic reference images for disease detection...")
    print("=" * 60)
    
    for disease in diseases:
        # Normalize disease name for folder creation
        safe_disease_name = disease.replace("/", "-")
        disease_dir = base_dir / safe_disease_name
        disease_dir.mkdir(exist_ok=True)
        
        # Generate 3 variations per disease for better matching
        for variation in range(3):
            img = generate_disease_image(disease)
            filename = disease_dir / f"reference_{variation + 1:02d}.jpg"
            img.save(filename, "JPEG", quality=85)
            print(f"Generated: {disease}/{filename.name}")
    
    print("\n" + "=" * 60)
    print(f"Generated reference images for {len(diseases)} diseases")
    print(f"Total images: {len(diseases) * 3}")
    print("\nRestart the backend to load new reference images")


if __name__ == "__main__":
    main()
