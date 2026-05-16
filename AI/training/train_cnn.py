import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split

# CNN Model for Poultry Disease Detection
# Classes: 12 poultry diseases for comprehensive detection

CLASSES = [
    "Newcastle disease",
    "Avian Influenza",
    "Infectious Bursal Disease",
    "Marek's Disease",
    "Fowl Pox",
    "Infectious Bronchitis",
    "Salmonellosis/Pullorum",
    "Fowl Cholera",
    "Mycoplasmosis (CRD)",
    "Infectious Coryza",
    "Coccidiosis",
    "Healthy",
]

IMG_SIZE = 224
NUM_CLASSES = len(CLASSES)


def create_cnn_model():
    """Build CNN with MobileNetV2 transfer learning"""
    base_model = keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    model = keras.Sequential(
        [
            layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3)),
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.3),
            layers.Dense(256, activation="relu"),
            layers.Dropout(0.2),
            layers.Dense(NUM_CLASSES, activation="softmax"),
        ]
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


def generate_synthetic_data(num_samples=500):
    """Generate synthetic training data with realistic disease patterns based on actual symptoms
    
    Disease visual characteristics based on provided poultry disease images:
    - Newcastle: Very dark head/body (respiratory distress)
    - Avian Influenza: Intense redness, head swelling
    - IBD: Pale, depressed, low contrast (immunosuppression)
    - Marek's: Pale/wasted with high texture variation (neurological)
    - Fowl Pox: Red scabby lesions with textured bumps
    - Infectious Bronchitis: Pale with nasal discharge signs
    - Salmonellosis: Greenish-brown diarrhea pattern
    - Fowl Cholera: Severe swelling, dark red appearance
    - Mycoplasmosis: Cloudy/misty pattern with some variation
    - Infectious Coryza: Facial swelling, purple-tinted redness
    - Coccidiosis: Bloody yellow-orange appearance
    - Healthy: Bright, balanced colors, high contrast
    """
    X = []
    y = []

    for class_idx in range(NUM_CLASSES):
        for _ in range(num_samples // NUM_CLASSES):
            img = np.random.rand(IMG_SIZE, IMG_SIZE, 3).astype(np.float32)
            
            # 0: Newcastle disease - VERY DARK with slight redness (respiratory collapse)
            if class_idx == 0:
                img *= 0.25  # Very dark/black
                img[:, :, 0] += 0.18  # Slight reddish tint (inflammation)
                # Add some edge variation for texture
                noise = np.random.rand(IMG_SIZE, IMG_SIZE, 3) * 0.08
                img += noise
                
            # 1: Avian Influenza - INTENSE RED with swelling (severe inflammation)
            elif class_idx == 1:
                img *= 0.5
                img[:, :, 0] += 0.60  # Very strong red channel
                img[:, :, 1] *= 0.55  # Lower green
                img[:, :, 2] *= 0.45  # Lower blue (purplish red)
                # Add local bright spots for swelling
                spots = np.random.rand(IMG_SIZE // 16, IMG_SIZE // 16) > 0.7
                spots_full = np.kron(spots, np.ones((16, 16)))
                h, w = spots_full.shape
                img[:h, :w, 0] += spots_full * 0.15
                
            # 2: Infectious Bursal Disease - PALE GREENISH (immunosuppression)
            elif class_idx == 2:
                img *= 0.65  # Lighter/lethargic
                img[:, :, 1] += 0.32  # Strong green tint
                img[:, :, 0] *= 0.75  # Lower red
                img[:, :, 2] *= 0.65  # Lower blue
                # Low contrast = depression
                img = img * 0.9 + 0.1  # Reduce contrast
                
            # 3: Marek's Disease - PALE WASTED with high variation (neurological damage)
            elif class_idx == 3:
                img *= 0.58  # Pale appearance
                # High texture variation from nerve damage
                texture = np.random.rand(IMG_SIZE, IMG_SIZE, 3) * 0.25
                img += texture
                img = np.clip(img, 0.2, 0.8)  # Clamp for pale but variable
                
            # 4: Fowl Pox - RED SCABBY LESIONS with bumpy texture
            elif class_idx == 4:
                img *= 0.6
                img[:, :, 0] += 0.48  # Red channel high
                img[:, :, 2] += 0.12  # Some blue (bruising from lesions)
                img[:, :, 1] *= 0.70  # Lower green
                # Create scabby texture
                for i in range(20):
                    y_pos = np.random.randint(0, IMG_SIZE-30)
                    x_pos = np.random.randint(0, IMG_SIZE-30)
                    img[y_pos:y_pos+30, x_pos:x_pos+30, 0] += 0.15
                    img[y_pos:y_pos+30, x_pos:x_pos+30, 1] *= 0.6
                
            # 5: Infectious Bronchitis - PALE with slight redness (nasal discharge)
            elif class_idx == 5:
                img *= 0.75  # Pale
                img[:, :, 0] += 0.18  # Slight reddish tint
                img[:, :, 1] += 0.18  # More white/pale greenish
                img[:, :, 2] *= 0.8
                # Add some discharge patterns
                img[:IMG_SIZE//3, :, 0] += np.random.rand(IMG_SIZE//3, IMG_SIZE) * 0.08
                
            # 6: Salmonellosis/Pullorum - GREENISH-BROWN DIARRHEA pattern
            elif class_idx == 6:
                img *= 0.6
                img[:, :, 1] += 0.28  # Green tint
                img[:, :, 0] += 0.22  # Brown-red tint
                img[:, :, 2] *= 0.55  # Lower blue
                # Diarrhea streaks
                for _ in range(15):
                    x = np.random.randint(0, IMG_SIZE)
                    img[x:x+50, :, 1] += 0.08
                    img[x:x+50, :, 0] += 0.05
                
            # 7: Fowl Cholera - SEVERE SWELLING with dark redness
            elif class_idx == 7:
                img *= 0.40  # Dark/severe
                img[:, :, 0] += 0.55  # Very strong red (swollen)
                img[:, :, 1] *= 0.45
                img[:, :, 2] *= 0.35
                # Swelling spots
                spots = np.random.rand(IMG_SIZE // 20, IMG_SIZE // 20) > 0.65
                spots_full = np.kron(spots, np.ones((20, 20)))
                h, w = spots_full.shape
                img[:h, :w, 0] += spots_full * 0.20
                
            # 8: Mycoplasmosis (CRD) - CLOUDY/MISTY appearance
            elif class_idx == 8:
                img = np.ones((IMG_SIZE, IMG_SIZE, 3)) * 0.52  # Grayish
                # Add slight cloudiness variations
                cloudiness = np.random.rand(IMG_SIZE, IMG_SIZE, 3) * 0.18
                img += cloudiness
                # Respiratory cloudiness pattern
                img[:, :, 0] += np.random.rand(IMG_SIZE, IMG_SIZE) * 0.06
                
            # 9: Infectious Coryza - FACIAL SWELLING with purple tint
            elif class_idx == 9:
                img *= 0.62
                img[:, :, 0] += 0.38  # Red from swelling
                img[:, :, 2] += 0.28  # Blue (purple-ish)
                img[:, :, 1] *= 0.65
                # Swelling in upper region (head)
                img[:IMG_SIZE//2, :, 0] += 0.08
                img[:IMG_SIZE//2, :, 2] += 0.06
                
            # 10: Coccidiosis - BLOODY YELLOW-ORANGE appearance
            elif class_idx == 10:
                img *= 0.55
                img[:, :, 0] += 0.45  # Red (blood)
                img[:, :, 1] += 0.42  # Yellow (diarrhea)
                img[:, :, 2] *= 0.25  # Very low blue
                # Blood and diarrhea streaks
                for _ in range(25):
                    x_pos = np.random.randint(50, IMG_SIZE-50)
                    y_pos = np.random.randint(50, IMG_SIZE-50)
                    img[x_pos:x_pos+40, y_pos:y_pos+40, 0] += 0.12
                    img[x_pos:x_pos+40, y_pos:y_pos+40, 1] += 0.08
                
            # 11: Healthy - BRIGHT, CLEAN, BALANCED colors
            else:
                img *= 1.20  # Brighter
                img = np.clip(img, 0, 1)
                # Add natural feather coloration variation
                feather_color = np.random.rand()
                if feather_color < 0.4:  # White
                    img = img * 0.95 + 0.15
                elif feather_color < 0.7:  # Brown
                    img[:, :, 0] += 0.15
                    img[:, :, 1] += 0.08
                else:  # Red
                    img[:, :, 0] += 0.10

            X.append(np.clip(img, 0, 1))
            y.append(class_idx)

    return np.array(X), keras.utils.to_categorical(y, NUM_CLASSES)


def train():
    print("🐔 PoultryGuard AI - CNN Training")
    print("=" * 50)

    print("\n📊 Generating synthetic dataset...")
    X, y = generate_synthetic_data(num_samples=2000)  # Increased for 12 classes
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")

    print("\n🏗️  Building CNN model...")
    model = create_cnn_model()
    model.summary()

    print("\n🎯 Training model...")
    # Increased epochs and better batch size for 12 classes
    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=20,  # Increased from 15 for better convergence with 12 classes
        batch_size=32,
        verbose=1,
    )

    print("\n💾 Saving model...")
    os.makedirs("../models", exist_ok=True)
    model.save("../models/poultry_cnn.keras")
    print("✅ Model saved to: ../models/poultry_cnn.keras")

    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    print(f"\n📈 Validation Accuracy: {val_acc * 100:.2f}%")
    print(f"📉 Validation Loss: {val_loss:.4f}")

    print("\n✨ Training complete!")


if __name__ == "__main__":
    train()
