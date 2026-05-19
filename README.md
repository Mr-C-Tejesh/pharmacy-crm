# Pharmacy CRM System — Premium DBMS Project

A robust, full-stack Pharmacy Management System designed for professional portfolio and DBMS college evaluation. This project features a modern React dashboard connected to a high-performance FastAPI backend, implementing a complex relational database structure for inventory, sales, and supplier management.

## 🚀 Project Overview
- **Pharmacy Inventory Management:** Comprehensive tracking of medical stock with automatic status updates.
- **Billing & Point-of-Sale (POS):** Real-time invoice generation with automatic stock deduction.
- **Supplier Management:** Centralized database for pharmaceutical vendors and procurement tracking.
- **Dashboard Analytics:** Real-time data visualization of sales performance and inventory health.
- **Real-time Stock Updates:** Synchronous database updates between sales and inventory levels.

## ✨ Features
- **Inventory CRUD:** Add, edit, and manage medicines with detailed batch and expiry tracking.
- **Billing System:** Multi-item invoice generation with payment mode selection.
- **Supplier Management:** Track vendors and associate them with specific inventory items.
- **Dashboard Statistics:** Live tracking of Total Sales, Items Sold, and Inventory Value.
- **Low Stock Alerts:** Automatic identification of medicines falling below the threshold (20 units).
- **Expiry Tracking:** Proactive status monitoring for expired or soon-to-expire stock.
- **Advanced Filtering:** Server-side search, status-based filtering, and pagination.
- **REST API Integration:** Clean separation of concerns with a modular API layer.

## 🛠 Tech Stack
- **Frontend:** React (Functional Components & Hooks), Vanilla CSS (Custom Variable System)
- **Backend:** FastAPI (Python), Pydantic (Validation), Uvicorn (ASGI)
- **Database:** SQLite (Relational modeling with SQLAlchemy ORM)
- **Deployment:** Render (Backend), Vercel (Frontend)

## 📂 Folder Structure
```text
pharmacy-crm/
├── backend/            # FastAPI Source Code
│   ├── app/            # Main application logic
│   │   ├── routers/    # API Route Controllers
│   │   ├── models.py   # SQLAlchemy DB Schema
│   │   └── crud.py     # DB Operations
│   └── pharmacy.db     # SQLite Database
├── frontend/           # React Source Code
│   ├── src/
│   │   ├── api/        # Service Layer
│   │   ├── components/ # Reusable UI
│   │   └── pages/      # View Modules
└── README.md
```

## 🗄 Database Design
The system uses a normalized relational schema to ensure data integrity and query efficiency:
- **Medicines:** Tracks batch numbers, generic names, quantities, and expiry dates.
- **Suppliers:** Stores vendor contact information and business details.
- **Sales:** Records invoice metadata, patient names, and total amounts.
- **SaleItems:** Junction table connecting sales to medicines with specific quantities.
- **Payments:** Tracks financial transactions linked to each sale.

### Relationships
- **One Supplier → Many Medicines:** Each medicine is linked to its primary vendor.
- **One Sale → Many Sale Items:** Support for multiple medicines in a single invoice.
- **One Sale → One Payment:** Every completed sale generates a corresponding payment record.

## 📊 ER Diagram
![ER Diagram](./assets/er-diagram.png)

---

## 🔌 API Endpoints

### Inventory
- `GET /inventory/` - List/Search medicines
- `POST /inventory/` - Add new stock
- `PUT /inventory/{id}` - Update medicine details

### Billing
- `GET /billing/` - View sales history
- `POST /billing/` - Generate new invoice and deduct stock

### Dashboard
- `GET /dashboard/summary` - Fetch real-time KPI statistics

### Suppliers
- `GET /suppliers/` - Manage vendor directory

---

## 💻 Local Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m app.seed  # Initialize sample data
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 🔗 Deployment Links
- **Frontend:** [https://pharmacy-crm-three.vercel.app/](https://pharmacy-crm-three.vercel.app/)
- **Backend:** [https://pharmacy-crm-api.onrender.com/](https://pharmacy-crm-api.onrender.com/)

## 📸 Screenshots
- **Dashboard:** ![Dashboard Placeholder](./assets/screenshots/dashboard.png)
- **Inventory:** ![Inventory Placeholder](./assets/screenshots/inventory.png)
- **Billing:** ![Billing Placeholder](./assets/screenshots/billing.png)
- **Suppliers:** ![Suppliers Placeholder](./assets/screenshots/suppliers.png)

## 🔮 Future Improvements
- **Authentication:** Role-based access for Pharmacists and Admins.
- **GST Billing:** Automatic tax calculation and GST-compliant invoicing.
- **Barcode Scanning:** Rapid stock entry and checkout using mobile camera/scanners.
- **PDF Export:** Generation of professional PDF receipts and monthly reports.
