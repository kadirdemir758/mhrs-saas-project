from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.location import Province, District

router = APIRouter(prefix="/locations", tags=["Locations"])

class ProvinceOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class DistrictOut(BaseModel):
    id: int
    name: str
    province_id: int

    class Config:
        from_attributes = True

@router.get("/provinces", response_model=List[ProvinceOut], summary="Bütün illeri listeler")
def get_provinces(db: Session = Depends(get_db)):
    """
    Veritabanındaki Türkiye'nin 81 ilini alfabe sırasına göre getirir.
    """
    return db.query(Province).order_by(Province.name).all()

@router.get("/districts", response_model=List[DistrictOut], summary="İle ait ilçeleri listeler")
def get_districts(province_id: int = Query(...), db: Session = Depends(get_db)):
    """
    Bir `province_id` (plaka veya veritabanı id) alır ve o ile ait tüm ilçeleri listeler.
    """
    return db.query(District).filter(District.province_id == province_id).order_by(District.name).all()
