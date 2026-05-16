"""
Image Reference Matcher - Compare uploaded images to disease reference images
"""
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from PIL import Image
from io import BytesIO
from collections import defaultdict
from threading import Lock


CANONICAL_DISEASE_NAMES = {
    "newcastle disease": "Newcastle-Disease",
    "newcastle-disease": "Newcastle-Disease",
    "avian influenza": "Avian-Influenza",
    "avian-influenza": "Avian-Influenza",
    "infectious bursal disease": "Infectious-Bursal-Disease",
    "infectious-bursal-disease": "Infectious-Bursal-Disease",
    "marek's disease": "Marek-Disease",
    "marek disease": "Marek-Disease",
    "marek-disease": "Marek-Disease",
    "fowl pox": "Fowl-Pox",
    "fowl-pox": "Fowl-Pox",
    "infectious bronchitis": "Infectious-Bronchitis",
    "infectious-bronchitis": "Infectious-Bronchitis",
    "salmonellosis/pullorum": "Salmonellosis-Pullorum",
    "salmonellosis pullorum": "Salmonellosis-Pullorum",
    "salmonellosis-pullorum": "Salmonellosis-Pullorum",
    "fowl cholera": "Fowl-Cholera",
    "fowl-cholera": "Fowl-Cholera",
    "mycoplasmosis (crd)": "Mycoplasmosis-CRD",
    "mycoplasmosis crd": "Mycoplasmosis-CRD",
    "mycoplasmosis-crd": "Mycoplasmosis-CRD",
    "infectious coryza": "Infectious-Coryza",
    "infectious-coryza": "Infectious-Coryza",
    "coccidiosis": "Coccidiosis",
    "healthy": "Healthy",
}

class ImageReferenceMatcher:
    """Match uploaded images against disease reference images using feature similarity"""
    
    def __init__(self, reference_dir: str | None = None):
        backend_root = Path(__file__).resolve().parents[2]
        sample_data_dir = backend_root.parent / "AI" / "sample_data"
        self.reference_dir = Path(reference_dir) if reference_dir else sample_data_dir
        self.disease_references: Dict[str, List[Dict]] = defaultdict(list)
        self._loaded_file_count = 0
        self._load_lock = Lock()
        self._loaded_once = False

    def _ensure_loaded(self):
        if self._loaded_once:
            return

        with self._load_lock:
            if self._loaded_once:
                return
            self.load_references()
            self._loaded_once = True

    def _normalize_disease_name(self, name: str) -> str:
        return CANONICAL_DISEASE_NAMES.get(name.strip().lower(), name.strip())
    
    def load_references(self):
        """Load all reference images from disease folders"""
        self.disease_references.clear()
        self._loaded_file_count = 0

        if not self.reference_dir.exists():
            print(f"Warning: Reference directory {self.reference_dir} does not exist")
            return
        
        # Iterate through disease folders
        for disease_folder in self.reference_dir.iterdir():
            if disease_folder.is_dir() and disease_folder.name != '__pycache__':
                disease_name = self._normalize_disease_name(disease_folder.name)
                image_files = (
                    list(disease_folder.glob('*.jpg'))
                    + list(disease_folder.glob('*.png'))
                    + list(disease_folder.glob('*.jpeg'))
                    + list(disease_folder.glob('*.webp'))
                )
                
                for img_path in image_files:
                    try:
                        with open(img_path, 'rb') as f:
                            img_data = f.read()
                        features = self._extract_features(img_data)
                        self.disease_references[disease_name].append({
                            'path': str(img_path),
                            'features': features
                        })
                        self._loaded_file_count += 1
                        print(f"[OK] Loaded reference: {disease_name}/{img_path.name}")
                    except Exception as e:
                        print(f"[FAIL] Failed to load {img_path}: {e}")
        
        print(f"\n[OK] Total diseases with references: {len(self.disease_references)}")
        for disease, refs in self.disease_references.items():
            print(f"  - {disease}: {len(refs)} image(s)")

    def _count_reference_files(self) -> int:
        if not self.reference_dir.exists():
            return 0

        total = 0
        for disease_folder in self.reference_dir.iterdir():
            if disease_folder.is_dir() and disease_folder.name != '__pycache__':
                total += len(list(disease_folder.glob('*.jpg')))
                total += len(list(disease_folder.glob('*.jpeg')))
                total += len(list(disease_folder.glob('*.png')))
                total += len(list(disease_folder.glob('*.webp')))
        return total
    
    def _extract_features(self, image_bytes: bytes) -> Dict:
        """Extract rich features including color, texture, edges, and spatial distribution"""
        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB").resize((224, 224))
            img_array = np.array(img, dtype=np.float32) / 255.0

            # 1. GLOBAL COLOR FEATURES
            red_ch   = float(np.mean(img_array[:, :, 0]))
            green_ch = float(np.mean(img_array[:, :, 1]))
            blue_ch  = float(np.mean(img_array[:, :, 2]))
            mean     = (red_ch + green_ch + blue_ch) / 3.0

            r_var = float(np.var(img_array[:, :, 0]))
            g_var = float(np.var(img_array[:, :, 1]))
            b_var = float(np.var(img_array[:, :, 2]))

            # 2. CONTRAST & TEXTURE
            grayscale = np.mean(img_array, axis=2)
            contrast  = float(np.std(grayscale))
            
            # Edge detection for texture information
            edges_h = np.abs(grayscale[1:, :] - grayscale[:-1, :])
            edges_v = np.abs(grayscale[:, 1:] - grayscale[:, :-1])
            edge_density = float(np.mean(np.concatenate([edges_h.flatten(), edges_v.flatten()])))

            # 3. COLOR DISTRIBUTION
            redness    = red_ch - green_ch
            yellowness = (red_ch + green_ch) - blue_ch
            
            # 4. QUADRANT ANALYSIS
            h, w = img_array.shape[:2]
            quad_means = [
                float(np.mean(img_array[:h//2, :w//2])),
                float(np.mean(img_array[:h//2, w//2:])),
                float(np.mean(img_array[h//2:, :w//2])),
                float(np.mean(img_array[h//2:, w//2:])),
            ]

            # 5. LOCAL PATTERN DISTRIBUTION (divide into 4x4 grid)
            grid_features = []
            for gi in range(4):
                for gj in range(4):
                    r1, c1 = (gi * h) // 4, (gj * w) // 4
                    r2, c2 = ((gi + 1) * h) // 4, ((gj + 1) * w) // 4
                    cell = img_array[r1:r2, c1:c2]
                    grid_features.append(float(np.mean(cell)))
                    grid_features.append(float(np.std(cell)))

            # 6. COLOR HISTOGRAMS (8-bin per channel)
            r_hist = np.histogram(img_array[:, :, 0], bins=8, range=(0, 1))[0].astype(float)
            g_hist = np.histogram(img_array[:, :, 1], bins=8, range=(0, 1))[0].astype(float)
            b_hist = np.histogram(img_array[:, :, 2], bins=8, range=(0, 1))[0].astype(float)
            r_hist /= r_hist.sum() + 1e-9
            g_hist /= g_hist.sum() + 1e-9
            b_hist /= b_hist.sum() + 1e-9

            return {
                "mean": mean,
                "red": red_ch,
                "green": green_ch,
                "blue": blue_ch,
                "r_var": r_var,
                "g_var": g_var,
                "b_var": b_var,
                "contrast": contrast,
                "edge_density": edge_density,
                "redness": redness,
                "yellowness": yellowness,
                "quad_means": quad_means,
                "grid_features": grid_features,
                "r_hist": r_hist.tolist(),
                "g_hist": g_hist.tolist(),
                "b_hist": b_hist.tolist(),
            }
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def _calculate_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate similarity using comprehensive feature comparison"""
        if not features1 or not features2:
            return 0.0

        # Global channel features
        global_keys = ['mean', 'red', 'green', 'blue', 'redness', 'yellowness', 'contrast', 'edge_density', 'r_var', 'g_var', 'b_var']
        global_dist = sum((features1.get(k, 0) - features2.get(k, 0)) ** 2 for k in global_keys)

        # Quadrant means distance (spatial distribution)
        q1 = features1.get("quad_means", [features1.get("mean", 0)] * 4)
        q2 = features2.get("quad_means", [features2.get("mean", 0)] * 4)
        quad_dist = sum((a - b) ** 2 for a, b in zip(q1, q2))

        # Grid features distance (local patterns)
        g1 = features1.get("grid_features", [0] * 32)
        g2 = features2.get("grid_features", [0] * 32)
        grid_dist = sum((a - b) ** 2 for a, b in zip(g1, g2))

        # Histogram distances (color distribution)
        def hist_dist(h1_list, h2_list):
            return sum((a - b) ** 2 for a, b in zip(h1_list, h2_list))

        rh_dist = hist_dist(
            features1.get("r_hist", [0.125] * 8),
            features2.get("r_hist", [0.125] * 8),
        )
        gh_dist = hist_dist(
            features1.get("g_hist", [0.125] * 8),
            features2.get("g_hist", [0.125] * 8),
        )
        bh_dist = hist_dist(
            features1.get("b_hist", [0.125] * 8),
            features2.get("b_hist", [0.125] * 8),
        )
        hist_total = rh_dist + gh_dist + bh_dist

        # Weighted composite distance (emphasis on diverse features)
        total_dist = (
            0.35 * np.sqrt(global_dist) +
            0.20 * np.sqrt(quad_dist) +
            0.20 * np.sqrt(grid_dist) +
            0.25 * np.sqrt(hist_total)
        )

        return 1.0 / (1.0 + total_dist)
    
    def find_best_match(self, image_bytes: bytes) -> Tuple[str, float, Dict]:
        """
        Find the best matching disease for uploaded image
        
        Returns:
            (disease_name, similarity_score, match_details)
        """
        self._ensure_loaded()

        # Auto-reload if new reference files were added after server startup
        current_file_count = self._count_reference_files()
        if current_file_count != self._loaded_file_count:
            self.load_references()

        if self._loaded_file_count == 0:
            return None, 0.0, {}

        # Extract features from uploaded image
        uploaded_features = self._extract_features(image_bytes)
        if not uploaded_features:
            return None, 0.0, {}
        
        best_disease = None
        best_similarity = -1
        best_ref_info = {}
        
        # Compare against all reference images
        for disease_name, references in self.disease_references.items():
            for ref_data in references:
                ref_features = ref_data['features']
                similarity = self._calculate_similarity(uploaded_features, ref_features)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_disease = disease_name
                    best_ref_info = {
                        'reference_path': ref_data['path'],
                        'similarity': similarity
                    }
        
        if best_disease:
            return best_disease, best_similarity, best_ref_info
        
        return None, 0.0, {}
    
    def get_loaded_diseases(self) -> List[str]:
        """Return list of diseases with loaded reference images"""
        return list(self.disease_references.keys())


# Global matcher instance
reference_matcher = ImageReferenceMatcher()
