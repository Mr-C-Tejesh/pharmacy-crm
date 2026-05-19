from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import Optional, List


# ── Supplier Schemas ─────────────────────────────────────────────────────────

class SupplierBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ── Medicine Schemas ─────────────────────────────────────────────────────────

class MedicineCreate(BaseModel):
    name:         str
    generic_name: str
    batch_no:     str
    expiry_date:  date
    quantity:     int
    price:        float
    supplier:     str  # Can be the name of the supplier
    supplier_id:  Optional[int] = None

    @validator("name", "generic_name", "batch_no", "supplier", pre=True)
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @validator("quantity")
    def quantity_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v

    @validator("price")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than zero")
        return v

    @validator("expiry_date")
    def expiry_must_be_valid(cls, v):
        return v


class MedicineUpdate(BaseModel):
    name:         Optional[str] = None
    generic_name: Optional[str] = None
    batch_no:     Optional[str] = None
    expiry_date:  Optional[date] = None
    quantity:     Optional[int] = None
    price:        Optional[float] = None
    supplier:     Optional[str] = None
    supplier_id:  Optional[int] = None

    @validator("name", "generic_name", "batch_no", "supplier", pre=True)
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @validator("quantity")
    def quantity_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("Quantity cannot be negative")
        return v

    @validator("price")
    def price_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than zero")
        return v


class StatusUpdate(BaseModel):
    status: str

    @validator("status")
    def must_be_valid_status(cls, v):
        allowed = ["Active", "Low Stock", "Expired", "Out of Stock"]
        if v not in allowed:
            raise ValueError(f"Status must be one of: {allowed}")
        return v


class MedicineResponse(BaseModel):
    id:             int
    name:           str
    generic_name:   str
    batch_no:       str
    expiry_date:    date
    quantity:       int
    price:          float
    supplier:       str
    supplier_id:    Optional[int]
    status:         str
    days_to_expiry: int
    created_at:     datetime
    updated_at:     datetime

    class Config:
        orm_mode = True


# ── Sale Schemas ─────────────────────────────────────────────────────────────

class SaleItemCreate(BaseModel):
    medicine_id: int
    quantity: int

class SaleCreate(BaseModel):
    patient_name: str
    payment_mode: str
    items: List[SaleItemCreate]

class SaleItemResponse(BaseModel):
    id:         int
    medicine_id: int
    quantity:   int
    unit_price: float

    class Config:
        orm_mode = True

class PaymentResponse(BaseModel):
    id: int
    amount: float
    payment_method: str
    status: str
    transaction_id: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class SaleResponse(BaseModel):
    id:           int
    invoice_no:   str
    patient_name: str
    payment_mode: str
    total_amount: float
    status:       str
    item_count:   int
    created_at:   datetime
    items:        Optional[List[SaleItemResponse]] = []
    payment:      Optional[PaymentResponse] = None

    class Config:
        orm_mode = True


# ── Paginated Response ───────────────────────────────────────────────────────

class PaginatedMedicines(BaseModel):
    data:        List[MedicineResponse]
    total:       int
    page:        int
    limit:       int
    total_pages: int
    has_next:    bool
    has_prev:    bool

class PaginatedSuppliers(BaseModel):
    data:        List[SupplierResponse]
    total:       int
    page:        int
    limit:       int
    total_pages: int
    has_next:    bool
    has_prev:    bool

class PaginatedSales(BaseModel):
    data:        List[SaleResponse]
    total:       int
    page:        int
    limit:       int
    total_pages: int
    has_next:    bool
    has_prev:    bool
