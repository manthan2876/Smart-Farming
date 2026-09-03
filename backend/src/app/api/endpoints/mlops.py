from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_admin_role
from app.core import get_session
from app.models.dataset import DatasetCandidate
import json
import zipfile
import os
import tempfile
from pathlib import Path

from pydantic import BaseModel
import shutil

class DatasetExportRequest(BaseModel):
    filters: dict
    split: dict
    format: str
    imageTarget: str

router = APIRouter(prefix="/admin/dataset", tags=["mlops", "dataset"])

@router.get("/summary")
async def get_dataset_summary(
    is_admin: bool = Depends(require_admin_role),
    session: Session = Depends(get_session)
):
    from sqlalchemy import func
    from app.models.prediction import Prediction
    from app.models.feedback import Feedback
    
    expert_overridden = session.query(DatasetCandidate).filter(DatasetCandidate.source == "expert_correction").count()
    farmer_confirmed = session.query(Feedback).filter(Feedback.is_correct == True).count()
    total_candidates = expert_overridden + farmer_confirmed
    
    return {
        "total": total_candidates,
        "expert_overridden": expert_overridden,
        "farmer_confirmed": farmer_confirmed
    }

@router.post("/export")
async def export_dataset_post(
    payload: DatasetExportRequest,
    user_id: str = Depends(get_current_user),
    is_admin: bool = Depends(require_admin_role),
    session: Session = Depends(get_session)
):
    candidates = session.query(DatasetCandidate).all()
    if not candidates:
        raise HTTPException(status_code=404, detail="No dataset candidates available")
        
    tmp_dir = Path(tempfile.gettempdir()) / "smartfarming_mlops_v2"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = tmp_dir / "dataset_export.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        metadata = []
        for c in candidates:
            img_path = Path("src") / c.image_path
            if img_path.exists():
                zipf.write(img_path, arcname=f"images/{img_path.name}")
                
            metadata.append({
                "id": c.id,
                "prediction_id": c.prediction_id,
                "source": c.source,
                "image_file": img_path.name if img_path.exists() else None,
                "original_label": c.original_label,
                "corrected_label": c.corrected_label,
                "status": c.status,
                "created_at": c.created_at.isoformat()
            })
            
        meta_path = tmp_dir / "metadata.json"
        with meta_path.open("w") as f:
            json.dump(metadata, f, indent=2)
            
        zipf.write(meta_path, arcname="metadata.json")
        
        config_path = tmp_dir / "export_config.json"
        with config_path.open("w") as f:
            json.dump(payload.model_dump(), f, indent=2)
            
        zipf.write(config_path, arcname="export_config.json")
        
    return FileResponse(path=zip_path, filename="dataset_export.zip", media_type="application/zip")

