from datetime import datetime, timezone, timedelta, date
from .database import SessionLocal
from . import models

IST = timezone(timedelta(hours=5, minutes=30))

def seed():
    db = SessionLocal()

    if db.query(models.Medicine).count() > 0:
        print("Database already has data — skipping seed.")
        db.close()
        return

    today = date.today()

    # Seed Suppliers
    suppliers = [
        models.Supplier(name="Micro Labs Ltd.", contact_person="Ramesh", phone="9876543210"),
        models.Supplier(name="GlaxoSmithKline India", contact_person="Suresh", phone="9876543211"),
        models.Supplier(name="Sun Pharmaceutical", contact_person="Mukesh", phone="9876543212"),
        models.Supplier(name="Aristo Pharmaceuticals", contact_person="Raj", phone="9876543213"),
        models.Supplier(name="Glenmark Pharmaceuticals", contact_person="Vijay", phone="9876543214"),
        models.Supplier(name="Alembic Pharmaceuticals", contact_person="Anil", phone="9876543215"),
        models.Supplier(name="Cipla Ltd.", contact_person="Sunil", phone="9876543216"),
        models.Supplier(name="Sanofi India", contact_person="Amit", phone="9876543217"),
        models.Supplier(name="USV Pvt. Ltd.", contact_person="Rahul", phone="9876543218"),
    ]
    db.add_all(suppliers)
    db.flush()

    sup_map = {s.name: s.id for s in suppliers}

    # Seed Medicines
    medicines = [
        models.Medicine(name="Dolo 650", generic_name="Paracetamol", batch_no="DL-2024-0341", expiry_date=today + timedelta(days=540), quantity=320, price=30.0, supplier="Micro Labs Ltd.", supplier_id=sup_map["Micro Labs Ltd."], status="Active"),
        models.Medicine(name="Augmentin 625", generic_name="Amoxicillin + Clavulanate", batch_no="AUG-2024-1192", expiry_date=today + timedelta(days=400), quantity=85, price=195.0, supplier="GlaxoSmithKline India", supplier_id=sup_map["GlaxoSmithKline India"], status="Active"),
        models.Medicine(name="Metformin 500mg", generic_name="Metformin Hydrochloride", batch_no="MET-2024-2234", expiry_date=today + timedelta(days=620), quantity=210, price=45.0, supplier="Sun Pharmaceutical", supplier_id=sup_map["Sun Pharmaceutical"], status="Active"),
        models.Medicine(name="Pantop 40", generic_name="Pantoprazole", batch_no="PAN-2024-3312", expiry_date=today + timedelta(days=480), quantity=150, price=85.0, supplier="Aristo Pharmaceuticals", supplier_id=sup_map["Aristo Pharmaceuticals"], status="Active"),
        models.Medicine(name="Telma 40", generic_name="Telmisartan", batch_no="TEL-2024-4401", expiry_date=today + timedelta(days=730), quantity=95, price=120.0, supplier="Glenmark Pharmaceuticals", supplier_id=sup_map["Glenmark Pharmaceuticals"], status="Active"),
        models.Medicine(name="Azithral 500", generic_name="Azithromycin", batch_no="AZI-2024-5521", expiry_date=today + timedelta(days=300), quantity=12, price=145.0, supplier="Alembic Pharmaceuticals", supplier_id=sup_map["Alembic Pharmaceuticals"], status="Low Stock"),
        models.Medicine(name="Calpol 250mg Syrup", generic_name="Paracetamol Suspension", batch_no="CAL-2024-6634", expiry_date=today + timedelta(days=180), quantity=7, price=55.0, supplier="GlaxoSmithKline India", supplier_id=sup_map["GlaxoSmithKline India"], status="Low Stock"),
        models.Medicine(name="Amoxil 250mg", generic_name="Amoxicillin", batch_no="AMX-2023-7745", expiry_date=today - timedelta(days=45), quantity=30, price=60.0, supplier="Cipla Ltd.", supplier_id=sup_map["Cipla Ltd."], status="Expired"),
        models.Medicine(name="Insulin Glargine", generic_name="Insulin Glargine", batch_no="INS-2024-8856", expiry_date=today + timedelta(days=200), quantity=0, price=980.0, supplier="Sanofi India", supplier_id=sup_map["Sanofi India"], status="Out of Stock"),
        models.Medicine(name="Ecosprin 75mg", generic_name="Aspirin", batch_no="ECO-2024-9967", expiry_date=today + timedelta(days=560), quantity=180, price=25.0, supplier="USV Pvt. Ltd.", supplier_id=sup_map["USV Pvt. Ltd."], status="Active"),
    ]

    db.add_all(medicines)
    db.flush()

    sales_data = [
        {
            "invoice_no":   "INV-2024-3001",
            "patient_name": "Arjun Sharma",
            "payment_mode": "UPI",
            "total_amount": 375.0,
            "status":       "Completed",
            "created_at":   datetime.now(IST).replace(tzinfo=None) - timedelta(hours=2),
            "items": [{"medicine": "Dolo 650", "qty": 2}, {"medicine": "Pantop 40", "qty": 1}]
        },
        {
            "invoice_no":   "INV-2024-3002",
            "patient_name": "Priya Venkatesh",
            "payment_mode": "Cash",
            "total_amount": 240.0,
            "status":       "Completed",
            "created_at":   datetime.now(IST).replace(tzinfo=None) - timedelta(hours=5),
            "items": [{"medicine": "Metformin 500mg", "qty": 1}, {"medicine": "Telma 40", "qty": 1}]
        },
    ]

    med_lookup = {m.name: m for m in medicines}

    for s in sales_data:
        sale = models.Sale(
            invoice_no=s["invoice_no"],
            patient_name=s["patient_name"],
            payment_mode=s["payment_mode"],
            total_amount=s["total_amount"],
            status=s["status"],
            created_at=s["created_at"],
        )
        db.add(sale)
        db.flush()

        for item in s["items"]:
            med = med_lookup[item["medicine"]]
            db.add(models.SaleItem(
                sale_id=sale.id,
                medicine_id=med.id,
                quantity=item["qty"],
                unit_price=med.price,
            ))
            
        db.add(models.Payment(
            sale_id=sale.id,
            amount=s["total_amount"],
            payment_method=s["payment_mode"],
            status="Completed"
        ))

    db.commit()
    print(f"Seeded {len(medicines)} medicines, {len(suppliers)} suppliers, and {len(sales_data)} sales.")
    db.close()

if __name__ == "__main__":
    seed()
