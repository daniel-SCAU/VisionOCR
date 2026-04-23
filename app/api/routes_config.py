from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db, get_settings
from app.schemas import SettingsResponse, SettingsUpdate, SettingItem
from app.models import Setting
from datetime import datetime

router = APIRouter()


@router.get("/config", response_model=SettingsResponse)
def get_config(db: Session = Depends(get_db), settings=Depends(get_settings)):
    rows = db.query(Setting).all()
    if not rows:
        defaults = settings.model_dump()
        items = [SettingItem(key=k, value=str(v)) for k, v in defaults.items()]
        return SettingsResponse(settings=items)
    items = [SettingItem(key=r.key, value=r.value) for r in rows]
    return SettingsResponse(settings=items)


@router.put("/config", response_model=SettingsResponse)
def update_config(payload: SettingsUpdate, db: Session = Depends(get_db)):
    for item in payload.settings:
        row = db.query(Setting).filter(Setting.key == item.key).first()
        if row:
            row.value = item.value
            row.updated_at = datetime.utcnow()
        else:
            db.add(Setting(key=item.key, value=item.value, updated_at=datetime.utcnow()))
    db.commit()
    rows = db.query(Setting).all()
    return SettingsResponse(settings=[SettingItem(key=r.key, value=r.value) for r in rows])
