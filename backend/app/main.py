from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from . import models
from .routers import inventory_router, dashboard_router, billing_router, suppliers_router
from .seed import seed

# create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pharmacy CRM API",
    description="REST API for managing pharmacy inventory, sales, and dashboard analytics.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory_router)
app.include_router(dashboard_router)
app.include_router(billing_router)
app.include_router(suppliers_router)


@app.on_event("startup")
def on_startup():
    # seed sample data on first run — skips if data already exists
    seed()


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "message": "Pharmacy CRM API is running",
        "docs": "/docs"
    }