from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import date, datetime, timezone, timedelta
from . import models, schemas
import uuid

IST = timezone(timedelta(hours=5, minutes=30))
def ist_now():
    return datetime.now(IST).replace(tzinfo=None)


# ── Status Logic ─────────────────────────────────────────────────────────────

def calculate_status(quantity: int, expiry_date: date) -> str:
    if expiry_date <= date.today():
        return "Expired"
    if quantity == 0:
        return "Out of Stock"
    if quantity < 20:
        return "Low Stock"
    return "Active"

def days_until_expiry(expiry_date: date) -> int:
    return (expiry_date - date.today()).days

def sync_medicine_status(db: Session, med: models.Medicine) -> models.Medicine:
    correct_status = calculate_status(med.quantity, med.expiry_date)
    if med.status != correct_status:
        med.status = correct_status
        db.commit()
        db.refresh(med)
    return med


# ── Supplier CRUD ─────────────────────────────────────────────────────────────

def get_suppliers(db: Session, search: str = None, page: int = 1, limit: int = 10) -> dict:
    query = db.query(models.Supplier)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            models.Supplier.name.ilike(term) |
            models.Supplier.contact_person.ilike(term)
        )
    total = query.count()
    total_pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    suppliers = query.order_by(models.Supplier.name).offset(offset).limit(limit).all()
    
    return {
        "data": suppliers,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }

def create_supplier(db: Session, supplier: schemas.SupplierCreate) -> models.Supplier:
    db_supplier = models.Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


# ── Medicine CRUD ─────────────────────────────────────────────────────────────

def get_medicine_by_id(db: Session, medicine_id: int) -> models.Medicine:
    med = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not med:
        raise HTTPException(
            status_code=404,
            detail={"error": "Medicine not found", "medicine_id": medicine_id}
        )
    return med

def get_medicines(db: Session, search: str = None, status: str = None, page: int = 1, limit: int = 10) -> dict:
    query = db.query(models.Medicine)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            models.Medicine.name.ilike(term)         |
            models.Medicine.generic_name.ilike(term) |
            models.Medicine.batch_no.ilike(term)     |
            models.Medicine.supplier.ilike(term)
        )
    if status:
        query = query.filter(models.Medicine.status == status)

    total = query.count()
    total_pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    medicines = query.order_by(models.Medicine.name).offset(offset).limit(limit).all()

    for med in medicines:
        sync_medicine_status(db, med)

    return {
        "data":        medicines,
        "total":       total,
        "page":        page,
        "limit":       limit,
        "total_pages": total_pages,
        "has_next":    page < total_pages,
        "has_prev":    page > 1,
    }

def create_medicine(db: Session, medicine: schemas.MedicineCreate) -> models.Medicine:
    existing = db.query(models.Medicine).filter(models.Medicine.batch_no == medicine.batch_no).first()
    if existing:
        raise HTTPException(status_code=400, detail={"error": "Batch number already exists"})

    data = medicine.dict()
    data["status"] = calculate_status(data["quantity"], data["expiry_date"])

    # If supplier string is provided, try to link or create supplier
    if data.get("supplier") and not data.get("supplier_id"):
        supplier_name = data["supplier"]
        sup = db.query(models.Supplier).filter(models.Supplier.name == supplier_name).first()
        if not sup:
            sup = models.Supplier(name=supplier_name)
            db.add(sup)
            db.flush()
        data["supplier_id"] = sup.id

    db_medicine = models.Medicine(**data)
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def update_medicine(db: Session, medicine_id: int, medicine: schemas.MedicineUpdate) -> models.Medicine:
    db_medicine = get_medicine_by_id(db, medicine_id)
    update_data = medicine.dict(exclude_unset=True)

    if "batch_no" in update_data:
        conflict = db.query(models.Medicine).filter(
            models.Medicine.batch_no == update_data["batch_no"],
            models.Medicine.id != medicine_id
        ).first()
        if conflict:
            raise HTTPException(status_code=400, detail={"error": "Batch number already in use"})

    if "supplier" in update_data and not update_data.get("supplier_id"):
        supplier_name = update_data["supplier"]
        sup = db.query(models.Supplier).filter(models.Supplier.name == supplier_name).first()
        if not sup:
            sup = models.Supplier(name=supplier_name)
            db.add(sup)
            db.flush()
        update_data["supplier_id"] = sup.id

    for key, value in update_data.items():
        setattr(db_medicine, key, value)

    db_medicine.status = calculate_status(db_medicine.quantity, db_medicine.expiry_date)
    db_medicine.updated_at = ist_now()

    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def update_medicine_status(db: Session, medicine_id: int, new_status: str) -> models.Medicine:
    db_medicine = get_medicine_by_id(db, medicine_id)
    db_medicine.status = new_status
    db_medicine.updated_at = ist_now()
    db.commit()
    db.refresh(db_medicine)
    return db_medicine


# ── Sales and Billing CRUD ─────────────────────────────────────────────────────────────

def create_sale(db: Session, sale: schemas.SaleCreate) -> models.Sale:
    total_amount = 0.0
    db_items = []
    
    for item in sale.items:
        med = get_medicine_by_id(db, item.medicine_id)
        if med.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for medicine {med.name}")
        
        # Deduct quantity
        med.quantity -= item.quantity
        sync_medicine_status(db, med)

        unit_price = med.price
        total_amount += unit_price * item.quantity
        db_items.append({
            "medicine_id": med.id,
            "quantity": item.quantity,
            "unit_price": unit_price
        })
    
    invoice_no = f"INV-{ist_now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
    
    db_sale = models.Sale(
        invoice_no=invoice_no,
        patient_name=sale.patient_name,
        payment_mode=sale.payment_mode,
        total_amount=total_amount,
        status="Completed",
        created_at=ist_now()
    )
    db.add(db_sale)
    db.flush()

    for item_data in db_items:
        db_sale_item = models.SaleItem(
            sale_id=db_sale.id,
            medicine_id=item_data["medicine_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"]
        )
        db.add(db_sale_item)
    
    # Create Payment
    db_payment = models.Payment(
        sale_id=db_sale.id,
        amount=total_amount,
        payment_method=sale.payment_mode,
        status="Completed"
    )
    db.add(db_payment)

    db.commit()
    db.refresh(db_sale)
    return db_sale

def get_sales(db: Session, page: int = 1, limit: int = 10) -> dict:
    query = db.query(models.Sale)
    total = query.count()
    total_pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    sales = query.order_by(models.Sale.created_at.desc()).offset(offset).limit(limit).all()
    
    # ensure items and payment are loaded or mapped
    return {
        "data": sales,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


# ── Dashboard Queries ─────────────────────────────────────────────────────────

def get_dashboard_summary(db: Session) -> dict:
    all_medicines = db.query(models.Medicine).all()
    for med in all_medicines:
        sync_medicine_status(db, med)

    total_items = len(all_medicines)
    low_stock   = sum(1 for m in all_medicines if m.status == "Low Stock")
    out_of_stock = sum(1 for m in all_medicines if m.status == "Out of Stock")
    expired     = sum(1 for m in all_medicines if m.status == "Expired")

    today = date.today()
    today_sales = db.query(func.sum(models.Sale.total_amount)).filter(
        func.date(models.Sale.created_at) == today
    ).scalar() or 0

    total_sales = db.query(func.sum(models.Sale.total_amount)).scalar() or 0

    items_sold_today = db.query(func.sum(models.SaleItem.quantity)).join(
        models.Sale
    ).filter(
        func.date(models.Sale.created_at) == today
    ).scalar() or 0

    total_items_sold = db.query(func.sum(models.SaleItem.quantity)).scalar() or 0

    return {
        "today_sales":      round(today_sales, 2),
        "total_sales":      round(total_sales, 2),
        "items_sold_today": items_sold_today,
        "total_items_sold": total_items_sold,
        "total_medicines":  total_items,
        "low_stock":        low_stock,
        "out_of_stock":     out_of_stock,
        "expired":          expired,
    }

def get_low_stock_items(db: Session) -> list:
    medicines = db.query(models.Medicine).filter(models.Medicine.quantity < 20).all()
    for med in medicines:
        sync_medicine_status(db, med)
    return medicines

def get_recent_sales(db: Session, limit: int = 10) -> list:
    return db.query(models.Sale).order_by(models.Sale.created_at.desc()).limit(limit).all()

def get_purchase_order_summary(db: Session) -> dict:
    needs_reorder = db.query(models.Medicine).filter(models.Medicine.quantity < 20).count()
    total_reorder_value = db.query(models.Medicine).filter(models.Medicine.quantity < 20).all()
    estimated_cost = sum((100 - m.quantity) * m.price for m in total_reorder_value if m.quantity < 20)
    return {
        "items_needing_reorder": needs_reorder,
        "estimated_reorder_cost": round(estimated_cost, 2),
        "pending_orders": 5,
    }

def get_inventory_overview(db: Session) -> dict:
    medicines = db.query(models.Medicine).all()
    for med in medicines:
        sync_medicine_status(db, med)

    total       = len(medicines)
    active      = sum(1 for m in medicines if m.status == "Active")
    low_stock   = sum(1 for m in medicines if m.status == "Low Stock")
    expired     = sum(1 for m in medicines if m.status == "Expired")
    out_of_stock = sum(1 for m in medicines if m.status == "Out of Stock")
    total_value = sum(m.price * m.quantity for m in medicines)

    return {
        "total_items":   total,
        "active_stock":  active,
        "low_stock":     low_stock,
        "expired":       expired,
        "out_of_stock":  out_of_stock,
        "total_value":   round(total_value, 2),
    }
