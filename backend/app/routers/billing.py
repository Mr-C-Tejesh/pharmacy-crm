from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from .. import crud, schemas

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)

@router.post("/", status_code=201)
def create_sale(
    sale: schemas.SaleCreate,
    db: Session = Depends(get_db)
):
    return crud.create_sale(db, sale)

@router.get("/")
def get_sales(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    result = crud.get_sales(db, page, limit)
    return result
