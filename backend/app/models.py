from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_person = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    medicines = relationship("Medicine", back_populates="supplier_rel")


class Medicine(Base):
    __tablename__ = "medicines"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    generic_name = Column(String, nullable=False)
    batch_no     = Column(String, nullable=False, unique=True)
    expiry_date  = Column(Date, nullable=False)
    quantity     = Column(Integer, nullable=False, default=0)
    price        = Column(Float, nullable=False)
    supplier     = Column(String, nullable=False) # Keep for backward compatibility/UI simplicity if needed, or deprecate. We will use supplier_id.
    supplier_id  = Column(Integer, ForeignKey("suppliers.id"), nullable=True)

    status = Column(String, nullable=False, default="Active")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sale_items = relationship("SaleItem", back_populates="medicine")
    supplier_rel = relationship("Supplier", back_populates="medicines")


class Sale(Base):
    __tablename__ = "sales"

    id           = Column(Integer, primary_key=True, index=True)
    invoice_no   = Column(String, nullable=False, unique=True)
    patient_name = Column(String, nullable=False)
    payment_mode = Column(String, nullable=False, default="Cash") # Legacy
    total_amount = Column(Float, nullable=False)
    status       = Column(String, nullable=False, default="Completed")
    created_at   = Column(DateTime, default=datetime.utcnow)

    items = relationship("SaleItem", back_populates="sale")
    payment = relationship("Payment", back_populates="sale", uselist=False)


class SaleItem(Base):
    __tablename__ = "sale_items"

    id          = Column(Integer, primary_key=True, index=True)
    sale_id     = Column(Integer, ForeignKey("sales.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    quantity    = Column(Integer, nullable=False)
    unit_price  = Column(Float, nullable=False)

    sale     = relationship("Sale", back_populates="items")
    medicine = relationship("Medicine", back_populates="sale_items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False) # Cash, Card, UPI
    status = Column(String, nullable=False, default="Completed")
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sale = relationship("Sale", back_populates="payment")
