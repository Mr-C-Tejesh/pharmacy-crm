from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from .. import crud, schemas

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)

@router.get("/")
def get_suppliers(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return crud.get_suppliers(db, search, page, limit)

@router.post("/", status_code=201)
def create_supplier(
    supplier: schemas.SupplierCreate,
    db: Session = Depends(get_db)
):
    return crud.create_supplier(db, supplier)
