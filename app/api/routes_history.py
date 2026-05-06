from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.deps import get_db
from app.schemas import InspectionResponse
from app.models import Inspection

router = APIRouter()


@router.get("/inspections", response_model=List[InspectionResponse])
def list_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Inspection)
    if status:
        q = q.filter(Inspection.status == status.upper())
    return q.order_by(Inspection.id.desc()).offset(skip).limit(limit).all()


@router.get("/inspections/{inspection_id}", response_model=InspectionResponse)
def get_inspection(inspection_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    row = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Inspection not found.")
    return row
