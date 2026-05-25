from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.farm import Farm
from app.models.image_prediction import ImagePrediction
from app.models.user import User
from app.schemas.prediction import ImagePredictionResponse
from app.services.alert_service import create_alert
from app.services.image_model_service import get_predictor
from app.services.image_reference_matcher import reference_matcher

router = APIRouter()
def _upload_dir() -> Path:
    import os
    if os.environ.get("NETLIFY") == "true" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        path = Path("/tmp/uploads")
    else:
        path = Path("uploads")
    path.mkdir(exist_ok=True, parents=True)
    return path

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

REFERENCE_FOLDER_MAP = {
    "Newcastle-Disease": "Newcastle-Disease",
    "Newcastle disease": "Newcastle-Disease",
    "Avian-Influenza": "Avian-Influenza",
    "Avian Influenza": "Avian-Influenza",
    "Infectious-Bursal-Disease": "Infectious-Bursal-Disease",
    "Infectious Bursal Disease": "Infectious-Bursal-Disease",
    "Marek-Disease": "Marek-Disease",
    "Marek's Disease": "Marek-Disease",
    "Fowl-Pox": "Fowl-Pox",
    "Fowl Pox": "Fowl-Pox",
    "Infectious-Bronchitis": "Infectious-Bronchitis",
    "Infectious Bronchitis": "Infectious-Bronchitis",
    "Salmonellosis-Pullorum": "Salmonellosis-Pullorum",
    "Salmonellosis/Pullorum": "Salmonellosis-Pullorum",
    "Fowl-Cholera": "Fowl-Cholera",
    "Fowl Cholera": "Fowl-Cholera",
    "Mycoplasmosis-CRD": "Mycoplasmosis-CRD",
    "Mycoplasmosis (CRD)": "Mycoplasmosis-CRD",
    "Infectious-Coryza": "Infectious-Coryza",
    "Infectious Coryza": "Infectious-Coryza",
    "Coccidiosis": "Coccidiosis",
    "Healthy": "Healthy",
}


def _reference_root_dir() -> Path:
    import os
    if os.environ.get("NETLIFY") == "true" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        base = Path("/tmp/disease_references")
    else:
        backend_root = Path(__file__).resolve().parents[3]
        base = backend_root / "disease_references"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _normalize_reference_disease_name(name: str) -> str:
    cleaned = (
        name.strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace("(", " ")
        .replace(")", " ")
    )
    cleaned = " ".join(cleaned.split())
    aliases = {
        "newcastle disease": "Newcastle-Disease",
        "newcastle-disease": "Newcastle-Disease",
        "avian influenza": "Avian-Influenza",
        "avian-influenza": "Avian-Influenza",
        "infectious bursal disease": "Infectious-Bursal-Disease",
        "infectious-bursal-disease": "Infectious-Bursal-Disease",
        "marek disease": "Marek-Disease",
        "marek's disease": "Marek-Disease",
        "marek-disease": "Marek-Disease",
        "fowl pox": "Fowl-Pox",
        "fowl-pox": "Fowl-Pox",
        "infectious bronchitis": "Infectious-Bronchitis",
        "infectious-bronchitis": "Infectious-Bronchitis",
        "salmonellosis pullorum": "Salmonellosis-Pullorum",
        "salmonellosis/pullorum": "Salmonellosis-Pullorum",
        "salmonellosis-pullorum": "Salmonellosis-Pullorum",
        "fowl cholera": "Fowl-Cholera",
        "fowl-cholera": "Fowl-Cholera",
        "mycoplasmosis crd": "Mycoplasmosis-CRD",
        "mycoplasmosis (crd)": "Mycoplasmosis-CRD",
        "mycoplasmosis-crd": "Mycoplasmosis-CRD",
        "infectious coryza": "Infectious-Coryza",
        "infectious-coryza": "Infectious-Coryza",
        "coccidiosis": "Coccidiosis",
        "healthy": "Healthy",
    }
    return aliases.get(cleaned, name.strip())


@router.post("/{farm_id}/image", response_model=ImagePredictionResponse)
async def predict_image(
    farm_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    extension = (file.filename or "image.jpg").split(".")[-1].lower()
    safe_filename = f"{uuid4().hex}.{extension}"
    image_path = _upload_dir() / safe_filename
    image_path.write_bytes(content)

    result = get_predictor().predict(content)

    prediction = ImagePrediction(
        farm_id=farm_id,
        image_path=str(image_path),
        disease_name=result["disease_name"],
        confidence=result["confidence"],
        risk_level=result["risk_level"],
        suggested_action=result["suggested_action"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    should_alert = (
        result["risk_level"] in {"Critical", "High", "Medium"}
        or result["confidence"] > settings.ALERT_CONFIDENCE_THRESHOLD
    )

    if should_alert:
        create_alert(
            db,
            farm_id,
            result["disease_name"],
            f"{result['disease_name']} detected with {round(result['confidence'] * 100, 2)}% confidence.",
            "Critical" if result["risk_level"] == "Critical" else "High" if result["risk_level"] == "High" else "Medium",
            "image_detection",
        )

    return prediction


@router.post("/reference-image")
async def upload_reference_image(
    disease_name: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")

    normalized_name = _normalize_reference_disease_name(disease_name)
    if normalized_name not in REFERENCE_FOLDER_MAP:
        raise HTTPException(status_code=400, detail="Invalid disease name")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    extension = (file.filename or "reference.jpg").split(".")[-1].lower()
    folder_name = REFERENCE_FOLDER_MAP[normalized_name]
    folder = _reference_root_dir() / folder_name
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}.{extension}"
    output_path = folder / filename
    output_path.write_bytes(content)

    reference_matcher.load_references()

    return {
        "message": "Reference image uploaded",
        "disease_name": normalized_name,
        "saved_path": str(output_path),
    }


@router.get("/reference-status")
async def reference_status(current_user: User = Depends(get_current_user)):
    reference_matcher.load_references()
    counts = {disease: len(items) for disease, items in reference_matcher.disease_references.items()}
    return {
        "total_diseases": len(counts),
        "total_images": sum(counts.values()),
        "counts": counts,
    }


@router.get("/reference-images/{disease_name}")
async def get_disease_reference_images(disease_name: str, current_user: User = Depends(get_current_user)):
    """Get list of reference images for a disease"""
    normalized_name = _normalize_reference_disease_name(disease_name)
    if normalized_name not in REFERENCE_FOLDER_MAP:
        raise HTTPException(status_code=400, detail="Invalid disease name")
    
    folder_name = REFERENCE_FOLDER_MAP[normalized_name]
    folder = _reference_root_dir() / folder_name
    
    if not folder.exists():
        return {"disease_name": normalized_name, "images": []}
    
    images = []
    for image_file in sorted(folder.glob("*")):
        if image_file.is_file() and image_file.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            images.append({
                "filename": image_file.name,
                "size": image_file.stat().st_size,
                "url": f"/api/predictions/reference-image-file/{folder_name}/{image_file.name}"
            })
    
    return {
        "disease_name": normalized_name,
        "folder_name": folder_name,
        "total_images": len(images),
        "images": images
    }


@router.get("/reference-image-file/{folder_name}/{filename}")
async def get_reference_image_file(folder_name: str, filename: str, current_user: User = Depends(get_current_user)):
    """Serve a disease reference image file"""
    # Validate folder name to prevent path traversal
    valid_folders = set(REFERENCE_FOLDER_MAP.values())
    if folder_name not in valid_folders:
        raise HTTPException(status_code=400, detail="Invalid folder name")
    
    # Validate filename to prevent path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    base_folder = _reference_root_dir() / folder_name
    image_path = base_folder / filename
    
    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Verify file is in the correct folder
    if not str(image_path).startswith(str(base_folder)):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    return FileResponse(
        path=image_path,
        media_type=f"image/{image_path.suffix.lower().strip('.')}"
    )
